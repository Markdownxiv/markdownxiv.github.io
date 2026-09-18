"""Public, answer-free samplers and exact witness checkers. Python 3.10+.

This module never constructs a solution, invokes a solver, or reads an answer key.
An index is a base-q encoding of INPUT COEFFICIENTS, not of a hidden witness.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import secrets
from pathlib import Path
from typing import Any

VERSION = 'witnessbench-prototype-1'
MAX_FILE_BYTES = 8_000_000

class ResourceLimit(ValueError):
    pass

def integer(x: Any, lo: int | None = None, hi: int | None = None) -> int:
    if type(x) is not int:
        raise ValueError('Expected an integer, not a boolean, float or string.')
    if x.bit_length() > 12000:
        raise ResourceLimit('Integer too large for this prototype.')
    if lo is not None and x < lo or hi is not None and x > hi:
        raise ValueError('Integer outside the allowed range.')
    return x

def exact_keys(x: Any, keys: set[str]) -> None:
    if type(x) is not dict or set(x) != keys:
        raise ValueError('Unexpected object fields.')

def vec(x: Any, n: int, lo: int, hi: int) -> list[int]:
    if type(x) is not list or len(x) != n:
        raise ValueError('Wrong vector length.')
    return [integer(a, lo, hi) for a in x]

def canonical(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()

def bind(x: dict) -> dict:
    return dict(x, instance_id=hashlib.sha256(canonical(x)).hexdigest())

def validate_instance(x: Any) -> dict:
    exact_keys(x, {'version', 'family', 'parameters', 'coefficients', 'instance_id'})
    body = {k: v for k, v in x.items() if k != 'instance_id'}
    if x['version'] != VERSION or x['instance_id'] != bind(body)['instance_id']:
        raise ValueError('Invalid version or instance digest.')
    p = x['parameters']
    if x['family'] == 'picard_fuchs':
        exact_keys(p, {'genus', 't_degree', 'bound'})
        g, h, b = integer(p['genus'], 1, 4), integer(p['t_degree'], 1, 3), integer(p['bound'], 1, 100)
        d = 2*g+1
        if type(x['coefficients']) is not list or len(x['coefficients']) != h:
            raise ValueError('Wrong coefficient array.')
        for row in x['coefficients']: vec(row, d, -b, b)
    elif x['family'] == 'isotropic':
        exact_keys(p, {'p', 'm', 'k', 'n'})
        prime = integer(p['p'])
        if prime not in (3, 5, 7): raise ValueError('Unsupported prime.')
        m, k = integer(p['m'], 1, 16), integer(p['k'], 1, 4)
        n = integer(p['n'], 1, 100)
        if n != (m+1)*k+m: raise ValueError('Dimension does not satisfy the sampler specification.')
        if type(x['coefficients']) is not list or len(x['coefficients']) != m:
            raise ValueError('Wrong number of matrices.')
        for row in x['coefficients']: vec(row, n*(n+1)//2, 0, prime-1)
    else:
        raise ValueError('Unknown family.')
    return x

def digits(index: int | None, base: int, count: int) -> list[int]:
    size = base**count
    if index is None: index = secrets.randbelow(size)
    if type(index) is not int or not 0 <= index < size:
        raise ValueError('Index must be an integer in [0, space_size).')
    out = []
    for _ in range(count):
        index, digit = divmod(index, base)
        out.append(digit)
    return out

def sample(family: str = 'picard_fuchs', *, index: int | None = None,
           genus: int = 2, t_degree: int = 1, bound: int = 3,
           p: int = 3, m: int = 8, k: int = 3) -> dict:
    """Sample uniformly if index=None; otherwise unrank the given input index.

    Arbitrarily large indices are supported. Full-support sampling is not
    restricted to a 64-bit or 256-bit pseudorandom seed.
    """
    if family == 'picard_fuchs':
        g, h, b = integer(genus, 1, 4), integer(t_degree, 1, 3), integer(bound, 1, 100)
        d = 2*g+1
        a = [v-b for v in digits(index, 2*b+1, d*h)]
        parameters = {'genus': g, 't_degree': h, 'bound': b}
        coefficients = [a[i*d:(i+1)*d] for i in range(h)]
    elif family == 'isotropic':
        prime = integer(p)
        if prime not in (3, 5, 7): raise ValueError('Unsupported prime.')
        m, k = integer(m, 1, 16), integer(k, 1, 4)
        n = (m+1)*k+m
        count = n*(n+1)//2
        a = digits(index, prime, m*count)
        parameters = {'p': prime, 'm': m, 'k': k, 'n': n}
        coefficients = [a[i*count:(i+1)*count] for i in range(m)]
    else:
        raise ValueError('Unknown family.')
    return bind({'version': VERSION, 'family': family,
                 'parameters': parameters, 'coefficients': coefficients})

def space_size(instance: dict) -> int:
    x = validate_instance(instance)
    p = x['parameters']
    if x['family'] == 'picard_fuchs':
        return (2*p['bound']+1)**((2*p['genus']+1)*p['t_degree'])
    return p['p']**(p['m']*p['n']*(p['n']+1)//2)

# Sparse integer polynomials in (t,x). These routines perform checks only.
Poly = dict[tuple[int, int], int]

def add(a: Poly, b: Poly, scale: int = 1) -> Poly:
    out = a.copy()
    for e, c in b.items():
        out[e] = out.get(e, 0) + scale*c
        if not out[e]: del out[e]
    if len(out) > 100000: raise ResourceLimit('Expanded polynomial is too large.')
    return out

def mul(a: Poly, b: Poly) -> Poly:
    if len(a)*len(b) > 25_000_000:
        raise ResourceLimit('Polynomial multiplication exceeds the prototype budget.')
    out: Poly = {}
    for (at, ax), ac in a.items():
        for (bt, bx), bc in b.items():
            e = (at+bt, ax+bx)
            out[e] = out.get(e, 0)+ac*bc
    return {e: c for e, c in out.items() if c}

def diff(a: Poly, axis: int) -> Poly:
    out = {}
    for e, c in a.items():
        if e[axis]:
            ee = list(e); ee[axis] -= 1
            out[tuple(ee)] = c*e[axis]
    return out

def scale(a: Poly, c: int) -> Poly:
    return {e: c*v for e, v in a.items() if c*v}

def read_poly(terms: Any, univariate: bool = False) -> Poly:
    if type(terms) is not list: raise ValueError('Polynomial must be a list of terms.')
    if len(terms) > 20000: raise ResourceLimit('Too many certificate terms.')
    out = {}
    for term in terms:
        if type(term) is not list or len(term) != (2 if univariate else 3):
            raise ValueError('Invalid polynomial term.')
        if univariate:
            a, c = term; b = 0
        else:
            a, b, c = term
        e = (integer(a, 0, 1000), integer(b, 0, 1000))
        c = integer(c)
        if not c or e in out: raise ValueError('Zero terms and duplicate exponents are not allowed.')
        out[e] = c
    return out

def q_polynomial(instance: dict) -> Poly:
    g = instance['parameters']['genus']
    q = {(0, 2*g+1): 1, (0, 0): -1}
    for i, row in enumerate(instance['coefficients'], 1):
        for j, c in enumerate(row):
            if c: q[(i, j)] = c
    return q

def check_picard_fuchs(instance: dict, submission: dict) -> bool:
    exact_keys(submission, {'instance_id', 'operator', 'certificate'})
    ops = submission['operator']
    if type(ops) is not list or not 2 <= len(ops) <= 2*instance['parameters']['genus']+1:
        raise ValueError('Operator order must be between 1 and 2g.')
    op = [read_poly(a, True) for a in ops]
    if not op[-1]: raise ValueError('The leading operator coefficient must be nonzero.')
    a = read_poly(submission['certificate'])
    r = len(op)-1
    q = q_polynomial(instance); qt = diff(q, 0); qx = diff(q, 1)
    powers = [{(0, 0): 1}]
    for _ in range(r): powers.append(mul(powers[-1], q))
    # G_j = 2^j Q^(j+1/2) (d/dt)^j Q^(-1/2), a differentiation identity.
    G = [{(0, 0): 1}]
    for j in range(r):
        G.append(add(scale(mul(q, diff(G[-1], 0)), 2),
                     mul(qt, G[-1]), -(2*j+1)))
    lhs: Poly = {}
    for j in range(r+1):
        lhs = add(lhs, mul(op[j], mul(G[j], powers[r-j])), 2**(r-j+1))
    rhs = scale(add(scale(mul(q, diff(a, 1)), 2), mul(qx, a), -(2*r-1)), 2**r)
    return lhs == rhs

def full_matrices(instance: dict) -> list[list[list[int]]]:
    n = instance['parameters']['n']
    matrices = []
    for row in instance['coefficients']:
        a = [[0]*n for _ in range(n)]
        h = 0
        for i in range(n):
            for j in range(i, n):
                a[i][j] = a[j][i] = row[h]; h += 1
        matrices.append(a)
    return matrices

def rank_mod(a: list[list[int]], p: int) -> int:
    b = [row[:] for row in a]
    if not b: return 0
    pivot = 0
    for col in range(len(b[0])):
        i = next((i for i in range(pivot, len(b)) if b[i][col] % p), None)
        if i is None: continue
        b[pivot], b[i] = b[i], b[pivot]
        inv = pow(b[pivot][col] % p, -1, p)
        b[pivot] = [(v*inv) % p for v in b[pivot]]
        for j in range(pivot+1, len(b)):
            c = b[j][col] % p
            if c: b[j] = [(v-c*w) % p for v, w in zip(b[j], b[pivot])]
        pivot += 1
        if pivot == len(b): break
    return pivot

def check_isotropic(instance: dict, submission: dict) -> bool:
    exact_keys(submission, {'instance_id', 'basis'})
    pars = instance['parameters']; p, n, k = pars['p'], pars['n'], pars['k']
    b = submission['basis']
    if type(b) is not list or len(b) != k:
        raise ValueError('Provide k basis vectors as rows.')
    b = [vec(row, n, 0, p-1) for row in b]
    if rank_mod(b, p) != k: return False
    for a in full_matrices(instance):
        for i in range(k):
            ab = [sum(c*v for c, v in zip(row, b[i])) % p for row in a]
            for j in range(i+1):
                if sum(c*v for c, v in zip(ab, b[j])) % p: return False
    return True

def verify(instance: Any, submission: Any) -> dict:
    """No key or solver. True means the submitted witness passes exact checks.

    Resource-limit results are not claims that the underlying mathematical
    answer is false. Deploy with OS-level CPU/memory limits for untrusted input.
    """
    try:
        validate_instance(instance)
        if type(submission) is not dict or submission.get('instance_id') != instance['instance_id']:
            raise ValueError('Submission is not bound to this instance.')
        accepted = (check_picard_fuchs(instance, submission)
                    if instance['family'] == 'picard_fuchs' else check_isotropic(instance, submission))
        return {'accepted': accepted, 'status': 'valid' if accepted else 'invalid_witness'}
    except ResourceLimit as e:
        return {'accepted': False, 'status': 'resource_limit', 'reason': str(e)}
    except (ValueError, TypeError, KeyError, OverflowError) as e:
        return {'accepted': False, 'status': 'invalid_format', 'reason': str(e)}

def markdown(instance: dict) -> str:
    validate_instance(instance)
    p = instance['parameters']
    header = f"# 数学构造题\n\n实例标识：`{instance['instance_id']}`\n\n"
    if instance['family'] == 'picard_fuchs':
        d = 2*p['genus']+1
        text = f"""令 $g={p['genus']}$，并定义
$$Q(t,x)=x^{{{d}}}-1+\\sum_{{i=1}}^{{{p['t_degree']}}}t^i\\sum_{{j=0}}^{{{d-1}}}c_{{ij}}x^j.$$
系数行从 $t^1$ 开始；每行从 $x^0$ 开始：

```json
{json.dumps(instance['coefficients'])}
```

求一个非零微分算子 $L=\\sum_{{j=0}}^r p_j(t)\\partial_t^j$，其中
$1\\le r\\le {2*p['genus']}$，$p_j\\in\\mathbb Z[t]$，$p_r\\ne0$，
并求 $A(t,x)\\in\\mathbb Z[t,x]$，使如下代数函数恒等式成立：
$$\\sum_{{j=0}}^r p_j(t)\\partial_t^j Q(t,x)^{{-1/2}}
=\\partial_x\\left(\\frac{{A(t,x)}}{{Q(t,x)^{{r-1/2}}}}\\right).$$
这里 $\\partial_t$ 保持 $x$ 不变，$\\partial_x$ 保持 $t$ 不变。
恒等式在 $\\mathbb Q(t,x)[y]/(y^2-Q)$ 中理解，$Q^{{-1/2}}=1/y$。
不要求算子阶数最小，也不要求解唯一。此参数族保证存在这种证书。

提交 JSON 字段为 `instance_id`、`operator`、`certificate`。
`operator[j]` 用 `[[t次数, 非零整数系数], ...]` 表示 $p_j$；
`certificate` 用 `[[t次数, x次数, 非零整数系数], ...]` 表示 $A$。
零多项式表示为 `[]`。同一多项式不得重复指数；整数不得用浮点数代替。
"""
    else:
        text = f"""在 $\\mathbb F_{{{p['p']}}}^{{{p['n']}}}$ 上给定 {p['m']} 个对称矩阵
$Q_1,\\ldots,Q_{{{p['m']}}}$。每个矩阵的上三角元按
$(0,0),(0,1),\\ldots,(0,n-1),(1,1),\\ldots,(n-1,n-1)$ 排列，
下三角由对称性确定。矩阵数据见随附同名 JSON 的 `coefficients`。

求 {p['k']} 个线性无关向量 $u_1,\\ldots,u_{{{p['k']}}}$，满足
$$u_a^\\mathsf{{T}}Q_i u_b=0\\quad
(1\\le i\\le {p['m']},\\;1\\le a,b\\le {p['k']}).$$
此参数族保证存在这样的向量。不能只检查 $a=b$ 的等式。

提交 JSON 字段为 `instance_id`、`basis`；`basis` 的每一行是一个基向量，
共 {p['k']} 行、每行 {p['n']} 个整数，元素必须属于
$\\{{0,\\ldots,{p['p']-1}\\}}$。不要求子空间唯一或维数最大。
"""
    return header+text

def _pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out: raise ValueError('Duplicate JSON key.')
        out[k] = v
    return out

def read_json(path: str) -> Any:
    p = Path(path)
    if p.stat().st_size > MAX_FILE_BYTES: raise ResourceLimit('File too large.')
    def reject_constant(s): raise ValueError('Non-finite JSON number.')
    return json.loads(p.read_text(encoding='utf-8'), object_pairs_hook=_pairs,
                      parse_constant=reject_constant)

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sam = sub.add_parser('sample')
    sam.add_argument('--family', choices=['picard_fuchs', 'isotropic'], required=True)
    sam.add_argument('--index', help='Optional input-coefficient index, decimal or 0x hexadecimal.')
    for name, default in [('genus',2),('t-degree',1),('bound',3),('p',3),('m',8),('k',3)]:
        sam.add_argument('--'+name, type=int, default=default)
    sam.add_argument('--out', required=True)
    sam.add_argument('--markdown')
    ver = sub.add_parser('verify'); ver.add_argument('instance'); ver.add_argument('submission')
    args = parser.parse_args()
    try:
        if args.command == 'sample':
            kwargs = vars(args).copy()
            out, md = kwargs.pop('out'), kwargs.pop('markdown'); kwargs.pop('command')
            if kwargs['index'] is not None: kwargs['index'] = int(kwargs['index'], 0)
            inst = sample(**kwargs)
            Path(out).write_text(json.dumps(inst, indent=2)+'\n', encoding='utf-8')
            if md: Path(md).write_text(markdown(inst), encoding='utf-8')
            print(json.dumps({'instance_id': inst['instance_id'], 'saved': out}))
        else:
            result = verify(read_json(args.instance), read_json(args.submission))
            print(json.dumps(result)); raise SystemExit(0 if result['accepted'] else 1)
    except (ValueError, OSError, TypeError) as e:
        print(json.dumps({'accepted': False, 'status': 'input_error', 'reason': str(e)}))
        raise SystemExit(2)

if __name__ == '__main__': main()
