# WAG-140 — Failure-domain independence

10 local tests passed in 0.005s, including 265 covering assignments of three nonempty labeled failure domains to three custodians. R is the minimum number of declared domains whose union covers all evidence custodians. Independent domains give R=3; a common host or administrator gives R=1. Unanimous availability cut is 1 in this model.

Scope: structural set-cover model, not live infrastructure inspection, probability estimation, cryptographic verification, or inventory integration. Every declared domain is assumed independently sufficient to erase all listed copies; all copies are assumed complete and surviving evidence observable. Hidden dependencies, threshold controls and selective withholding are not modeled. Exhaustive enumeration scales exponentially. Next WAG-141: separate availability, evidence erasure and conflicting-certificate thresholds.
