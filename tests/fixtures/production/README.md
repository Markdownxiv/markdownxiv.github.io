This is an **offline test fixture**, not a deployed archive or published paper.

The PoW was actually mined locally using the measured target in the copied
calibration. Its nonce and both production-size mathematical certificates are
real and independently verifiable. `experiment.json` records the measured local
mining duration. The registry's publication state is explicitly simulated for
offline testing; it is not a claim of successful GitHub Pages deployment.

Repository ID `1`, user ID `2`, the epoch, receipt time and body are test inputs.
CI verifies the saved proof and certificates; it performs no production mining
and does not invoke a production solver. These files are outside the real
`challenges/` registry and cannot enable the real production entry point.
