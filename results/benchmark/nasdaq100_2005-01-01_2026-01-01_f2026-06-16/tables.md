# Benchmark tables — nasdaq100_2005-01-01_2026-01-01_f2026-06-16
_smoke=False_  ·  folds=3

## Table A — directional / trading (fold-mean)

| method | split | category | horizon | n_windows | n_trades | acc | always_up_acc | excess_acc | balanced_acc | mcc | sharpe | max_drawdown | hit_rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| always_up | held_out | stock | 128 | 207 | 207 | 0.7105 | 0.7105 | 0.0000 | 0.5000 | 0.0000 | 0.5458 | -0.5941 | 0.7105 |
| always_up | held_out | stock | 16 | 207 | 207 | 0.5447 | 0.5447 | 0.0000 | 0.5000 | 0.0000 | 0.6080 | -0.3762 | 0.5447 |
| always_up | held_out | stock | 2 | 207 | 207 | 0.4458 | 0.4458 | 0.0000 | 0.5000 | 0.0000 | -1.2351 | -0.3433 | 0.4458 |
| always_up | held_out | stock | 32 | 207 | 207 | 0.6226 | 0.6226 | 0.0000 | 0.5000 | 0.0000 | 1.0696 | -0.3213 | 0.6226 |
| always_up | held_out | stock | 4 | 207 | 207 | 0.4175 | 0.4175 | 0.0000 | 0.5000 | 0.0000 | -1.2308 | -0.4620 | 0.4175 |
| always_up | held_out | stock | 64 | 207 | 207 | 0.5411 | 0.5411 | 0.0000 | 0.5000 | 0.0000 | 0.1240 | -0.6786 | 0.5411 |
| always_up | held_out | stock | 8 | 206 | 207 | 0.5771 | 0.5771 | 0.0000 | 0.5000 | 0.0000 | 0.9327 | -0.2606 | 0.5742 |
| always_up | seen | etf | 128 | 9 | 9 | 0.7778 | 0.7778 | 0.0000 | 0.8333 | 0.0000 | 5.2575 | -0.1050 | 0.7778 |
| always_up | seen | etf | 16 | 9 | 9 | 0.6667 | 0.6667 | 0.0000 | 0.5000 | 0.0000 | 1.1290 | -0.0679 | 0.6667 |
| always_up | seen | etf | 2 | 9 | 9 | 0.5556 | 0.5556 | 0.0000 | 0.6667 | 0.0000 | 0.5174 | -0.0209 | 0.5556 |
| always_up | seen | etf | 32 | 9 | 9 | 0.6667 | 0.6667 | 0.0000 | 0.6667 | 0.0000 | 2.5833 | -0.0469 | 0.6667 |
| always_up | seen | etf | 4 | 9 | 9 | 0.4444 | 0.4444 | 0.0000 | 0.5000 | 0.0000 | 6.2534 | -0.0412 | 0.4444 |
| always_up | seen | etf | 64 | 9 | 9 | 0.4444 | 0.4444 | 0.0000 | 0.5000 | 0.0000 | 0.0305 | -0.1290 | 0.4444 |
| always_up | seen | etf | 8 | 9 | 9 | 0.6667 | 0.6667 | 0.0000 | 0.6667 | 0.0000 | 2.5985 | -0.0186 | 0.6667 |
| always_up | seen | stock | 128 | 630 | 630 | 0.6531 | 0.6531 | 0.0000 | 0.5000 | 0.0000 | 0.5107 | -0.7154 | 0.6531 |
| always_up | seen | stock | 16 | 629 | 630 | 0.5840 | 0.5840 | 0.0000 | 0.5000 | 0.0000 | 0.6887 | -0.5672 | 0.5831 |
| always_up | seen | stock | 2 | 625 | 630 | 0.4762 | 0.4762 | 0.0000 | 0.5000 | 0.0000 | -0.7345 | -0.5575 | 0.4723 |
| always_up | seen | stock | 32 | 630 | 630 | 0.6396 | 0.6396 | 0.0000 | 0.5000 | 0.0000 | 0.7852 | -0.5307 | 0.6396 |
| always_up | seen | stock | 4 | 626 | 630 | 0.4693 | 0.4693 | 0.0000 | 0.5000 | 0.0000 | -0.3313 | -0.6682 | 0.4662 |
| always_up | seen | stock | 64 | 630 | 630 | 0.5064 | 0.5064 | 0.0000 | 0.5000 | 0.0000 | 0.0906 | -0.9221 | 0.5064 |
| always_up | seen | stock | 8 | 626 | 630 | 0.6024 | 0.6024 | 0.0000 | 0.5000 | 0.0000 | 1.4543 | -0.2974 | 0.5988 |
| ar1 | held_out | stock | 128 | 207 | 207 | 0.6470 | 0.7105 | -0.0635 | 0.4996 | -0.0146 | 0.1746 | -0.9177 | 0.6470 |
| ar1 | held_out | stock | 16 | 207 | 207 | 0.4970 | 0.5447 | -0.0477 | 0.4677 | -0.0840 | -0.0237 | -0.5806 | 0.4970 |
| ar1 | held_out | stock | 2 | 207 | 207 | 0.4884 | 0.4458 | 0.0425 | 0.5459 | 0.1012 | -0.1870 | -0.3179 | 0.4884 |
| ar1 | held_out | stock | 32 | 207 | 207 | 0.5212 | 0.6226 | -0.1014 | 0.4242 | -0.2129 | 0.3329 | -0.6335 | 0.5212 |
| ar1 | held_out | stock | 4 | 207 | 207 | 0.4324 | 0.4175 | 0.0150 | 0.4829 | -0.0376 | -0.9937 | -0.4609 | 0.4324 |
| ar1 | held_out | stock | 64 | 207 | 207 | 0.4920 | 0.5411 | -0.0492 | 0.4603 | -0.1170 | -0.2228 | -0.9362 | 0.4920 |
| ar1 | held_out | stock | 8 | 206 | 207 | 0.5188 | 0.5771 | -0.0583 | 0.4669 | -0.0786 | 0.0082 | -0.4141 | 0.5160 |
| ar1 | seen | etf | 128 | 9 | 9 | 0.6667 | 0.7778 | -0.1111 | 0.6667 | -0.3333 | 4.5188 | -0.1975 | 0.6667 |
| ar1 | seen | etf | 16 | 9 | 9 | 0.5556 | 0.6667 | -0.1111 | 0.4167 | -0.1667 | 0.2678 | -0.0825 | 0.5556 |
| ar1 | seen | etf | 2 | 9 | 9 | 0.4444 | 0.5556 | -0.1111 | 0.4722 | -0.1667 | -1.5460 | -0.0238 | 0.4444 |
| ar1 | seen | etf | 32 | 9 | 9 | 0.5556 | 0.6667 | -0.1111 | 0.5833 | -0.1667 | 2.0629 | -0.0523 | 0.5556 |
| ar1 | seen | etf | 4 | 9 | 9 | 0.2222 | 0.4444 | -0.2222 | 0.2222 | -0.3333 | -30.8126 | -0.0604 | 0.2222 |
| ar1 | seen | etf | 64 | 9 | 9 | 0.3333 | 0.4444 | -0.1111 | 0.3333 | -0.3333 | -1.1004 | -0.1758 | 0.3333 |
| ar1 | seen | etf | 8 | 9 | 9 | 0.5556 | 0.6667 | -0.1111 | 0.5833 | -0.1667 | 0.7701 | -0.0297 | 0.5556 |
| ar1 | seen | stock | 128 | 630 | 630 | 0.5766 | 0.6531 | -0.0765 | 0.4630 | -0.0853 | 0.1827 | -0.9409 | 0.5766 |
| ar1 | seen | stock | 16 | 629 | 630 | 0.5182 | 0.5840 | -0.0658 | 0.4646 | -0.0736 | 0.0743 | -0.6831 | 0.5175 |
| ar1 | seen | stock | 2 | 625 | 630 | 0.5085 | 0.4762 | 0.0323 | 0.5384 | 0.0808 | 0.4240 | -0.4939 | 0.5046 |
| ar1 | seen | stock | 32 | 630 | 630 | 0.5656 | 0.6396 | -0.0741 | 0.4711 | -0.0640 | 0.3246 | -0.7307 | 0.5656 |
| ar1 | seen | stock | 4 | 626 | 630 | 0.4647 | 0.4693 | -0.0046 | 0.4775 | -0.0447 | -0.5682 | -0.6280 | 0.4621 |
| ar1 | seen | stock | 64 | 630 | 630 | 0.4665 | 0.5064 | -0.0399 | 0.4596 | -0.0844 | -0.0730 | -0.9254 | 0.4665 |
| ar1 | seen | stock | 8 | 626 | 630 | 0.5304 | 0.6024 | -0.0720 | 0.4689 | -0.0651 | 0.4040 | -0.5077 | 0.5276 |
| persistence | held_out | stock | 128 | 206 | 206 | 0.4932 | 0.7094 | -0.2162 | 0.4314 | -0.1201 | 0.0953 | -0.8275 | 0.4932 |
| persistence | held_out | stock | 16 | 206 | 206 | 0.4427 | 0.5426 | -0.1000 | 0.4399 | -0.1230 | -0.2297 | -0.6969 | 0.4427 |
| persistence | held_out | stock | 2 | 206 | 206 | 0.4935 | 0.4468 | 0.0467 | 0.4779 | -0.0671 | 0.3452 | -0.2455 | 0.4935 |
| persistence | held_out | stock | 32 | 206 | 206 | 0.5323 | 0.6212 | -0.0890 | 0.5069 | 0.0261 | 0.1905 | -0.6069 | 0.5323 |
| persistence | held_out | stock | 4 | 206 | 206 | 0.4927 | 0.4144 | 0.0784 | 0.5002 | -0.0107 | 0.5186 | -0.2836 | 0.4927 |
| persistence | held_out | stock | 64 | 206 | 206 | 0.5341 | 0.5390 | -0.0050 | 0.5256 | 0.0522 | 0.0798 | -0.7912 | 0.5341 |
| persistence | held_out | stock | 8 | 205 | 206 | 0.5313 | 0.5754 | -0.0441 | 0.5215 | 0.0412 | -0.0110 | -0.4390 | 0.5290 |
| persistence | seen | etf | 128 | 9 | 9 | 0.5556 | 0.7778 | -0.2222 | 0.5833 | 0.1667 | 0.2145 | -0.1704 | 0.5556 |
| persistence | seen | etf | 16 | 9 | 9 | 0.4444 | 0.6667 | -0.2222 | 0.4167 | -0.1667 | 2.4789 | -0.0478 | 0.4444 |
| persistence | seen | etf | 2 | 9 | 9 | 0.7778 | 0.5556 | 0.2222 | 0.8056 | 0.5000 | 4.1102 | -0.0192 | 0.7778 |
| persistence | seen | etf | 32 | 9 | 9 | 0.6667 | 0.6667 | 0.0000 | 0.6389 | 0.1667 | 3.5252 | -0.0455 | 0.6667 |
| persistence | seen | etf | 4 | 9 | 9 | 0.6667 | 0.4444 | 0.2222 | 0.6944 | 0.1667 | 3.3276 | -0.0203 | 0.6667 |
| persistence | seen | etf | 64 | 9 | 9 | 0.4444 | 0.4444 | 0.0000 | 0.4167 | -0.1667 | 0.1826 | -0.0960 | 0.4444 |
| persistence | seen | etf | 8 | 9 | 9 | 0.6667 | 0.6667 | 0.0000 | 0.6389 | 0.1667 | 1.3235 | -0.0253 | 0.6667 |
| persistence | seen | stock | 128 | 619 | 619 | 0.5407 | 0.6556 | -0.1148 | 0.5120 | 0.0280 | 0.1917 | -0.9127 | 0.5407 |
| persistence | seen | stock | 16 | 619 | 619 | 0.5446 | 0.5842 | -0.0396 | 0.5304 | 0.0623 | 0.4663 | -0.7002 | 0.5446 |
| persistence | seen | stock | 2 | 619 | 619 | 0.5260 | 0.4782 | 0.0478 | 0.4948 | -0.0180 | 1.0086 | -0.4218 | 0.5260 |
| persistence | seen | stock | 32 | 619 | 619 | 0.5790 | 0.6386 | -0.0596 | 0.5588 | 0.1189 | 0.5476 | -0.6824 | 0.5790 |
| persistence | seen | stock | 4 | 619 | 619 | 0.5624 | 0.4705 | 0.0919 | 0.5424 | 0.0824 | 1.2762 | -0.3064 | 0.5624 |
| persistence | seen | stock | 64 | 619 | 619 | 0.5360 | 0.5093 | 0.0267 | 0.5351 | 0.0716 | 0.2027 | -0.8793 | 0.5360 |
| persistence | seen | stock | 8 | 619 | 619 | 0.5594 | 0.6034 | -0.0440 | 0.5466 | 0.0951 | 0.6060 | -0.6037 | 0.5594 |
| pooled | held_out | stock | 128 | 207 | 207 | 0.6297 | 0.7105 | -0.0808 | 0.4482 | -0.1456 | 0.4325 | -0.6711 | 0.6297 |
| pooled | held_out | stock | 16 | 207 | 207 | 0.5506 | 0.5447 | 0.0059 | 0.5481 | 0.1243 | 0.4960 | -0.4482 | 0.5506 |
| pooled | held_out | stock | 2 | 207 | 207 | 0.4818 | 0.4458 | 0.0360 | 0.5152 | 0.0048 | 0.6279 | -0.2605 | 0.4818 |
| pooled | held_out | stock | 32 | 207 | 207 | 0.6236 | 0.6226 | 0.0010 | 0.5357 | 0.0870 | 0.9932 | -0.3166 | 0.6236 |
| pooled | held_out | stock | 4 | 207 | 207 | 0.4782 | 0.4175 | 0.0608 | 0.5098 | 0.0337 | 0.1195 | -0.3568 | 0.4782 |
| pooled | held_out | stock | 64 | 207 | 207 | 0.5409 | 0.5411 | -0.0002 | 0.5114 | 0.0183 | 0.1519 | -0.6734 | 0.5409 |
| pooled | held_out | stock | 8 | 206 | 207 | 0.5533 | 0.5771 | -0.0238 | 0.5209 | 0.0422 | 0.8313 | -0.2980 | 0.5508 |
| pooled | seen | etf | 128 | 9 | 9 | 0.7778 | 0.7778 | 0.0000 | 0.8333 | 0.0000 | 5.2575 | -0.1050 | 0.7778 |
| pooled | seen | etf | 16 | 9 | 9 | 0.5556 | 0.6667 | -0.1111 | 0.5000 | 0.0000 | 0.4415 | -0.0687 | 0.5556 |
| pooled | seen | etf | 2 | 9 | 9 | 0.6667 | 0.5556 | 0.1111 | 0.6667 | 0.0000 | -0.2992 | -0.0243 | 0.6667 |
| pooled | seen | etf | 32 | 9 | 9 | 0.5556 | 0.6667 | -0.1111 | 0.5556 | 0.0000 | 0.7940 | -0.0620 | 0.5556 |
| pooled | seen | etf | 4 | 9 | 9 | 0.4444 | 0.4444 | 0.0000 | 0.4167 | -0.1667 | 6.0740 | -0.0424 | 0.4444 |
| pooled | seen | etf | 64 | 9 | 9 | 0.4444 | 0.4444 | 0.0000 | 0.5000 | 0.0000 | 0.0305 | -0.1290 | 0.4444 |
| pooled | seen | etf | 8 | 9 | 9 | 0.5556 | 0.6667 | -0.1111 | 0.6389 | 0.1667 | -0.1574 | -0.0344 | 0.5556 |
| pooled | seen | stock | 128 | 630 | 630 | 0.6171 | 0.6531 | -0.0359 | 0.4894 | -0.0193 | 0.3889 | -0.8528 | 0.6171 |
| pooled | seen | stock | 16 | 629 | 630 | 0.5535 | 0.5840 | -0.0305 | 0.5204 | 0.0425 | 0.3148 | -0.7601 | 0.5527 |
| pooled | seen | stock | 2 | 625 | 630 | 0.4827 | 0.4762 | 0.0065 | 0.4878 | -0.0365 | 0.2120 | -0.4690 | 0.4789 |
| pooled | seen | stock | 32 | 630 | 630 | 0.6082 | 0.6396 | -0.0315 | 0.5147 | 0.0361 | 0.6567 | -0.6887 | 0.6082 |
| pooled | seen | stock | 4 | 626 | 630 | 0.4939 | 0.4693 | 0.0246 | 0.4852 | -0.0314 | 0.2579 | -0.4843 | 0.4906 |
| pooled | seen | stock | 64 | 630 | 630 | 0.4938 | 0.5064 | -0.0126 | 0.4854 | -0.0468 | 0.0681 | -0.9576 | 0.4938 |
| pooled | seen | stock | 8 | 626 | 630 | 0.5866 | 0.6024 | -0.0158 | 0.5401 | 0.0877 | 1.2324 | -0.3864 | 0.5829 |
| random_walk | held_out | stock | 128 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | held_out | stock | 16 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | held_out | stock | 2 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | held_out | stock | 32 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | held_out | stock | 4 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | held_out | stock | 64 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | held_out | stock | 8 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | etf | 128 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | etf | 16 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | etf | 2 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | etf | 32 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | etf | 4 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | etf | 64 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | etf | 8 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | stock | 128 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | stock | 16 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | stock | 2 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | stock | 32 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | stock | 4 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | stock | 64 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| random_walk | seen | stock | 8 | 0 | 0 |  |  |  |  |  |  | 0.0000 |  |
| zero_shot | held_out | stock | 128 | 207 | 207 | 0.5590 | 0.7105 | -0.1515 | 0.4993 | -0.0033 | 0.2215 | -0.8424 | 0.5590 |
| zero_shot | held_out | stock | 16 | 207 | 207 | 0.5275 | 0.5447 | -0.0172 | 0.5140 | 0.0334 | 0.3613 | -0.4557 | 0.5275 |
| zero_shot | held_out | stock | 2 | 207 | 207 | 0.3988 | 0.4458 | -0.0470 | 0.4376 | -0.1409 | -1.9845 | -0.3994 | 0.3988 |
| zero_shot | held_out | stock | 32 | 207 | 207 | 0.5603 | 0.6226 | -0.0623 | 0.5327 | 0.0634 | 0.3151 | -0.5950 | 0.5603 |
| zero_shot | held_out | stock | 4 | 207 | 207 | 0.4106 | 0.4175 | -0.0069 | 0.4573 | -0.1038 | -1.0371 | -0.4283 | 0.4106 |
| zero_shot | held_out | stock | 64 | 207 | 207 | 0.5304 | 0.5411 | -0.0107 | 0.5201 | 0.0417 | 0.0768 | -0.8725 | 0.5304 |
| zero_shot | held_out | stock | 8 | 206 | 207 | 0.5240 | 0.5771 | -0.0531 | 0.5048 | 0.0099 | 0.1818 | -0.4024 | 0.5215 |
| zero_shot | seen | etf | 128 | 9 | 9 | 0.7778 | 0.7778 | 0.0000 | 0.8333 | 0.0000 | 5.2575 | -0.1050 | 0.7778 |
| zero_shot | seen | etf | 16 | 9 | 9 | 0.3333 | 0.6667 | -0.3333 | 0.2500 | -0.5000 | -0.8010 | -0.0944 | 0.3333 |
| zero_shot | seen | etf | 2 | 9 | 9 | 0.4444 | 0.5556 | -0.1111 | 0.4722 | -0.1667 | -6.9476 | -0.0378 | 0.4444 |
| zero_shot | seen | etf | 32 | 9 | 9 | 0.6667 | 0.6667 | -0.0000 | 0.6389 | 0.1667 | 0.8445 | -0.0608 | 0.6667 |
| zero_shot | seen | etf | 4 | 9 | 9 | 0.3333 | 0.4444 | -0.1111 | 0.3333 | -0.3333 | -26.8220 | -0.0538 | 0.3333 |
| zero_shot | seen | etf | 64 | 9 | 9 | 0.4444 | 0.4444 | 0.0000 | 0.5000 | 0.0000 | -0.1411 | -0.1199 | 0.4444 |
| zero_shot | seen | etf | 8 | 9 | 9 | 0.2222 | 0.6667 | -0.4444 | 0.2222 | -0.6667 | -4.8862 | -0.0523 | 0.2222 |
| zero_shot | seen | stock | 128 | 630 | 630 | 0.4924 | 0.6531 | -0.1606 | 0.4704 | -0.0632 | 0.0291 | -1.0000 | 0.4924 |
| zero_shot | seen | stock | 16 | 629 | 630 | 0.5199 | 0.5840 | -0.0641 | 0.4925 | -0.0167 | 0.0463 | -0.8024 | 0.5192 |
| zero_shot | seen | stock | 2 | 625 | 630 | 0.4947 | 0.4762 | 0.0185 | 0.5022 | 0.0035 | 0.1185 | -0.4572 | 0.4908 |
| zero_shot | seen | stock | 32 | 630 | 630 | 0.5257 | 0.6396 | -0.1139 | 0.4865 | -0.0257 | 0.1138 | -0.9106 | 0.5257 |
| zero_shot | seen | stock | 4 | 626 | 630 | 0.4543 | 0.4693 | -0.0151 | 0.4777 | -0.0616 | -0.7633 | -0.7025 | 0.4515 |
| zero_shot | seen | stock | 64 | 630 | 630 | 0.4888 | 0.5064 | -0.0176 | 0.4880 | -0.0247 | 0.0672 | -0.9627 | 0.4888 |
| zero_shot | seen | stock | 8 | 626 | 630 | 0.5098 | 0.6024 | -0.0926 | 0.4792 | -0.0453 | 0.2150 | -0.5855 | 0.5067 |

## Table B — point forecast (fold-mean, macro-averaged)

| method | split | category | n_windows | MAE | RMSE | sMAPE | MASE |
|---|---|---|---|---|---|---|---|
| always_up | held_out | stock | 207 | 24.9112 | 32.2330 | 0.1244 | 33.3387 |
| always_up | seen | etf | 9 | 30.2974 | 37.2059 | 0.0915 | 38.7373 |
| always_up | seen | stock | 630 | 21.3510 | 27.0971 | 0.1363 | 35.8891 |
| ar1 | held_out | stock | 207 | 28.5403 | 38.0870 | 0.1326 | 35.9333 |
| ar1 | seen | etf | 9 | 37.9105 | 46.7786 | 0.1041 | 44.8608 |
| ar1 | seen | stock | 630 | 24.3815 | 31.5046 | 0.1479 | 42.2222 |
| pooled | held_out | stock | 207 | 25.1533 | 32.9602 | 0.1211 | 32.6081 |
| pooled | seen | etf | 9 | 29.0814 | 35.6195 | 0.0862 | 36.5375 |
| pooled | seen | stock | 630 | 21.7924 | 28.1156 | 0.1362 | 36.4541 |
| random_walk | held_out | stock | 207 | 24.9128 | 32.2340 | 0.1245 | 33.3421 |
| random_walk | seen | etf | 9 | 30.3016 | 37.2105 | 0.0915 | 38.7428 |
| random_walk | seen | stock | 630 | 21.3522 | 27.0983 | 0.1363 | 35.8914 |
| zero_shot | held_out | stock | 207 | 26.4355 | 34.2398 | 0.1275 | 33.9985 |
| zero_shot | seen | etf | 9 | 32.4895 | 41.4590 | 0.0966 | 42.1775 |
| zero_shot | seen | stock | 630 | 23.3190 | 29.7227 | 0.1459 | 39.3671 |

## Table C — calibration (fold-mean)

| method | split | category | quantile_level | nominal | empirical_coverage | pinball |
|---|---|---|---|---|---|---|
| pooled | held_out | stock | 0.0500 | 0.0500 | 0.4356 | 12.7596 |
| pooled | held_out | stock | 0.1000 | 0.1000 | 0.1608 | 6.9411 |
| pooled | held_out | stock | 0.2000 | 0.2000 | 0.2426 | 9.8404 |
| pooled | held_out | stock | 0.3000 | 0.3000 | 0.3146 | 11.5290 |
| pooled | held_out | stock | 0.4000 | 0.4000 | 0.3890 | 12.4092 |
| pooled | held_out | stock | 0.5000 | 0.5000 | 0.4671 | 12.5767 |
| pooled | held_out | stock | 0.6000 | 0.6000 | 0.5442 | 12.1309 |
| pooled | held_out | stock | 0.7000 | 0.7000 | 0.6289 | 11.0312 |
| pooled | held_out | stock | 0.8000 | 0.8000 | 0.7063 | 9.1345 |
| pooled | held_out | stock | 0.9000 | 0.9000 | 0.8049 | 6.0665 |
| pooled | seen | etf | 0.0500 | 0.0500 | 0.3984 | 15.6101 |
| pooled | seen | etf | 0.1000 | 0.1000 | 0.1866 | 8.5253 |
| pooled | seen | etf | 0.2000 | 0.2000 | 0.2847 | 11.9629 |
| pooled | seen | etf | 0.3000 | 0.3000 | 0.3264 | 13.8700 |
| pooled | seen | etf | 0.4000 | 0.4000 | 0.3819 | 14.6432 |
| pooled | seen | etf | 0.5000 | 0.5000 | 0.4280 | 14.5407 |
| pooled | seen | etf | 0.6000 | 0.6000 | 0.5009 | 13.6410 |
| pooled | seen | etf | 0.7000 | 0.7000 | 0.5599 | 11.8200 |
| pooled | seen | etf | 0.8000 | 0.8000 | 0.6701 | 8.9404 |
| pooled | seen | etf | 0.9000 | 0.9000 | 0.8394 | 5.1293 |
| pooled | seen | stock | 0.0500 | 0.0500 | 0.4573 | 10.5691 |
| pooled | seen | stock | 0.1000 | 0.1000 | 0.1657 | 5.0072 |
| pooled | seen | stock | 0.2000 | 0.2000 | 0.2635 | 7.7443 |
| pooled | seen | stock | 0.3000 | 0.3000 | 0.3403 | 9.5136 |
| pooled | seen | stock | 0.4000 | 0.4000 | 0.4130 | 10.5397 |
| pooled | seen | stock | 0.5000 | 0.5000 | 0.4845 | 10.8962 |
| pooled | seen | stock | 0.6000 | 0.6000 | 0.5574 | 10.6433 |
| pooled | seen | stock | 0.7000 | 0.7000 | 0.6327 | 9.7309 |
| pooled | seen | stock | 0.8000 | 0.8000 | 0.7155 | 8.0593 |
| pooled | seen | stock | 0.9000 | 0.9000 | 0.8154 | 5.3585 |
| zero_shot | held_out | stock | 0.0500 | 0.0500 | 0.4039 | 12.0954 |
| zero_shot | held_out | stock | 0.1000 | 0.1000 | 0.1251 | 7.1301 |
| zero_shot | held_out | stock | 0.2000 | 0.2000 | 0.2097 | 10.2760 |
| zero_shot | held_out | stock | 0.3000 | 0.3000 | 0.2879 | 12.0754 |
| zero_shot | held_out | stock | 0.4000 | 0.4000 | 0.3637 | 12.9937 |
| zero_shot | held_out | stock | 0.5000 | 0.5000 | 0.4403 | 13.2178 |
| zero_shot | held_out | stock | 0.6000 | 0.6000 | 0.5188 | 12.8178 |
| zero_shot | held_out | stock | 0.7000 | 0.7000 | 0.5978 | 11.7135 |
| zero_shot | held_out | stock | 0.8000 | 0.8000 | 0.6905 | 9.7231 |
| zero_shot | held_out | stock | 0.9000 | 0.9000 | 0.8075 | 6.4861 |
| zero_shot | seen | etf | 0.0500 | 0.0500 | 0.4062 | 14.9303 |
| zero_shot | seen | etf | 0.1000 | 0.1000 | 0.1615 | 10.5776 |
| zero_shot | seen | etf | 0.2000 | 0.2000 | 0.2127 | 13.4131 |
| zero_shot | seen | etf | 0.3000 | 0.3000 | 0.3012 | 14.9015 |
| zero_shot | seen | etf | 0.4000 | 0.4000 | 0.3819 | 15.8801 |
| zero_shot | seen | etf | 0.5000 | 0.5000 | 0.4557 | 16.2447 |
| zero_shot | seen | etf | 0.6000 | 0.6000 | 0.5026 | 15.7368 |
| zero_shot | seen | etf | 0.7000 | 0.7000 | 0.5755 | 13.8989 |
| zero_shot | seen | etf | 0.8000 | 0.8000 | 0.7066 | 10.6869 |
| zero_shot | seen | etf | 0.9000 | 0.9000 | 0.8620 | 6.9765 |
| zero_shot | seen | stock | 0.0500 | 0.0500 | 0.4271 | 10.0208 |
| zero_shot | seen | stock | 0.1000 | 0.1000 | 0.1469 | 5.3009 |
| zero_shot | seen | stock | 0.2000 | 0.2000 | 0.2388 | 8.2698 |
| zero_shot | seen | stock | 0.3000 | 0.3000 | 0.3145 | 10.1654 |
| zero_shot | seen | stock | 0.4000 | 0.4000 | 0.3863 | 11.2960 |
| zero_shot | seen | stock | 0.5000 | 0.5000 | 0.4569 | 11.6595 |
| zero_shot | seen | stock | 0.6000 | 0.6000 | 0.5316 | 11.3464 |
| zero_shot | seen | stock | 0.7000 | 0.7000 | 0.6104 | 10.3590 |
| zero_shot | seen | stock | 0.8000 | 0.8000 | 0.7005 | 8.6059 |
| zero_shot | seen | stock | 0.9000 | 0.9000 | 0.8082 | 5.7711 |

## Table D — significance (primary test flagged ★)

| comparison | split | horizon | test | statistic | p | fdr_adjusted | fdr_reject | n |
|---|---|---|---|---|---|---|---|---|
| pooled vs always_up | held_out | 2 | mcnemar | 0.0000 | 1.0000 | 1.0000 | False | 3 |
| pooled vs always_up | held_out | 2 | mcnemar | 0.0635 | 0.8013 | 0.8742 | False | 63 |
| pooled vs always_up | held_out | 2 | mcnemar | 10.0833 | 0.0005 | 0.0059 | True | 12 |
| pooled vs always_up | held_out | 4 | mcnemar | 0.5000 | 1.0000 | 1.0000 | False | 2 |
| pooled vs always_up | held_out | 4 | mcnemar | 0.0851 | 0.7709 | 0.8520 | False | 47 |
| pooled vs always_up | held_out | 4 | mcnemar | 6.7500 | 0.0063 | 0.0410 | True | 12 |
| pooled vs always_up | held_out | 8 | mcnemar | 0.1000 | 0.7539 | 0.8520 | False | 10 |
| pooled vs always_up | held_out | 8 | mcnemar | 0.0889 | 0.7660 | 0.8520 | False | 45 |
| pooled vs always_up | held_out | 8 | mcnemar | 1.1364 | 0.2863 | 0.5433 | False | 22 |
| pooled vs always_up | held_out | 16 | mcnemar | 2.5000 | 0.1094 | 0.3168 | False | 10 |
| pooled vs always_up | held_out | 16 | mcnemar | 0.5952 | 0.4408 | 0.6857 | False | 42 |
| pooled vs always_up | held_out | 16 | mcnemar | 0.0000 | 1.0000 | 1.0000 | False | 17 |
| pooled vs always_up | held_out | 32 | mcnemar | 0.1667 | 1.0000 | 1.0000 | False | 6 |
| pooled vs always_up | held_out | 32 | mcnemar | 0.5161 | 0.4731 | 0.7097 | False | 31 |
| pooled vs always_up | held_out | 32 | mcnemar | 1.2308 | 0.2668 | 0.5433 | False | 13 |
| pooled vs always_up | held_out | 64 | mcnemar | 0.1667 | 0.6875 | 0.8520 | False | 6 |
| pooled vs always_up | held_out | 64 | mcnemar | 0.2105 | 0.6476 | 0.8463 | False | 19 |
| pooled vs always_up | held_out | 64 | mcnemar | 0.0000 | 1.0000 | 1.0000 | False | 13 |
| pooled vs always_up | held_out | 128 | mcnemar | 1.3333 | 0.2500 | 0.5385 | False | 3 |
| pooled vs always_up | held_out | 128 | mcnemar | 0.9000 | 0.3438 | 0.5775 | False | 10 |
| pooled vs always_up | held_out | 128 | mcnemar | 8.1000 | 0.0020 | 0.0182 | True | 10 |
| pooled vs zero_shot | held_out | 2 | diebold_mariano | -2.0485 | 0.0405 | 0.1480 | False | 66 |
| pooled vs zero_shot | held_out | 2 | diebold_mariano | 0.0055 | 0.9956 | 1.0000 | False | 69 |
| pooled vs zero_shot | held_out | 2 | diebold_mariano | 0.3045 | 0.7608 | 0.8520 | False | 72 |
| pooled vs zero_shot | held_out | 4 | diebold_mariano | -0.7938 | 0.4273 | 0.6857 | False | 66 |
| pooled vs zero_shot | held_out | 4 | diebold_mariano | -1.2917 | 0.1965 | 0.4460 | False | 69 |
| pooled vs zero_shot | held_out | 4 | diebold_mariano | -1.6300 | 0.1031 | 0.3093 | False | 72 |
| pooled vs zero_shot | held_out | 8 | diebold_mariano | -0.3179 | 0.7506 | 0.8520 | False | 66 |
| pooled vs zero_shot | held_out | 8 | diebold_mariano | -1.3015 | 0.1931 | 0.4460 | False | 69 |
| pooled vs zero_shot | held_out | 8 | diebold_mariano | -2.5452 | 0.0109 | 0.0573 | False | 72 |
| pooled vs zero_shot | held_out | 16 | diebold_mariano | -0.5904 | 0.5549 | 0.7547 | False | 66 |
| pooled vs zero_shot | held_out | 16 | diebold_mariano | -0.5954 | 0.5516 | 0.7547 | False | 69 |
| pooled vs zero_shot | held_out | 16 | diebold_mariano | -2.9874 | 0.0028 | 0.0215 | True | 72 |
| pooled vs zero_shot | held_out | 32 | diebold_mariano | -2.2788 | 0.0227 | 0.0907 | False | 66 |
| pooled vs zero_shot | held_out | 32 | diebold_mariano | -0.6049 | 0.5452 | 0.7547 | False | 69 |
| pooled vs zero_shot | held_out | 32 | diebold_mariano | -2.1488 | 0.0316 | 0.1208 | False | 72 |
| pooled vs zero_shot | held_out | 64 | diebold_mariano | -0.7783 | 0.4364 | 0.6857 | False | 66 |
| pooled vs zero_shot | held_out | 64 | diebold_mariano | -2.6432 | 0.0082 | 0.0493 | True | 69 |
| pooled vs zero_shot | held_out | 64 | diebold_mariano | -8.3287 | 0.0000 | 0.0000 | True | 72 |
| pooled vs zero_shot | held_out | 128 | diebold_mariano | -6.4739 | 0.0000 | 0.0000 | True | 66 |
| pooled vs zero_shot | held_out | 128 | diebold_mariano | -2.3682 | 0.0179 | 0.0883 | False | 69 |
| pooled vs zero_shot | held_out | 128 | diebold_mariano | -1.3358 | 0.1816 | 0.4359 | False | 72 |
| pooled vs always_up | seen | 2 | mcnemar | 1.2308 | 0.2668 | 0.5433 | False | 13 |
| pooled vs always_up | seen | 2 | mcnemar | 0.1404 | 0.7079 | 0.8520 | False | 178 |
| pooled vs always_up | seen | 2 | mcnemar | 6.6176 | 0.0090 | 0.0506 | False | 34 |
| pooled vs always_up | seen | 4 | mcnemar | 1.0667 | 0.3018 | 0.5433 | False | 15 |
| pooled vs always_up | seen | 4 | mcnemar | 0.7407 | 0.3895 | 0.6415 | False | 135 |
| pooled vs always_up | seen | 4 | mcnemar | 2.8929 | 0.0872 | 0.2712 | False | 28 |
| pooled vs always_up | seen | 8 | mcnemar | 1.8286 | 0.1755 | 0.4335 | False | 35 |
| pooled vs always_up | seen | 8 | mcnemar | 0.3451 | 0.5571 | 0.7547 | False | 142 |
| pooled vs always_up | seen | 8 | mcnemar | 1.1228 | 0.2892 | 0.5433 | False | 57 |
| pooled vs always_up | seen | 16 | mcnemar | 1.8286 | 0.1755 | 0.4335 | False | 35 |
| pooled vs always_up | seen | 16 | mcnemar | 0.1203 | 0.7289 | 0.8520 | False | 133 |
| pooled vs always_up | seen | 16 | mcnemar | 0.3137 | 0.5758 | 0.7678 | False | 51 |
| pooled vs always_up | seen | 32 | mcnemar | 1.3889 | 0.2379 | 0.5258 | False | 18 |
| pooled vs always_up | seen | 32 | mcnemar | 0.0430 | 0.8358 | 0.9001 | False | 93 |
| pooled vs always_up | seen | 32 | mcnemar | 2.3256 | 0.1263 | 0.3422 | False | 43 |
| pooled vs always_up | seen | 64 | mcnemar | 1.0667 | 0.3018 | 0.5433 | False | 15 |
| pooled vs always_up | seen | 64 | mcnemar | 0.1552 | 0.6940 | 0.8520 | False | 58 |
| pooled vs always_up | seen | 64 | mcnemar | 0.9730 | 0.3240 | 0.5670 | False | 37 |
| pooled vs always_up | seen | 128 | mcnemar | 0.1000 | 0.7539 | 0.8520 | False | 10 |
| pooled vs always_up | seen | 128 | mcnemar | 2.2500 | 0.1325 | 0.3478 | False | 36 |
| pooled vs always_up | seen | 128 | mcnemar | 4.0000 | 0.0433 | 0.1515 | False | 25 |
| pooled vs zero_shot | seen | 2 | diebold_mariano | -1.0454 | 0.2958 | 0.5433 | False | 201 |
| pooled vs zero_shot | seen | 2 | diebold_mariano | 1.5556 | 0.1198 | 0.3354 | False | 210 |
| pooled vs zero_shot | seen | 2 | diebold_mariano | 3.2436 | 0.0012 | 0.0124 | True | 219 |
| pooled vs zero_shot | seen | 4 | diebold_mariano | -2.3034 | 0.0213 | 0.0907 | False | 201 |
| pooled vs zero_shot | seen | 4 | diebold_mariano | -0.3312 | 0.7405 | 0.8520 | False | 210 |
| pooled vs zero_shot | seen | 4 | diebold_mariano | -0.4470 | 0.6549 | 0.8463 | False | 219 |
| pooled vs zero_shot | seen | 8 | diebold_mariano | -2.2959 | 0.0217 | 0.0907 | False | 201 |
| pooled vs zero_shot | seen | 8 | diebold_mariano | -0.6122 | 0.5404 | 0.7547 | False | 210 |
| pooled vs zero_shot | seen | 8 | diebold_mariano | -2.7529 | 0.0059 | 0.0410 | True | 219 |
| pooled vs zero_shot | seen | 16 | diebold_mariano | -2.2884 | 0.0221 | 0.0907 | False | 201 |
| pooled vs zero_shot | seen | 16 | diebold_mariano | -1.0279 | 0.3040 | 0.5433 | False | 210 |
| pooled vs zero_shot | seen | 16 | diebold_mariano | -1.9497 | 0.0512 | 0.1721 | False | 219 |
| pooled vs zero_shot | seen | 32 | diebold_mariano | -5.7415 | 0.0000 | 0.0000 | True | 201 |
| pooled vs zero_shot | seen | 32 | diebold_mariano | -0.6412 | 0.5214 | 0.7547 | False | 210 |
| pooled vs zero_shot | seen | 32 | diebold_mariano | -1.8103 | 0.0702 | 0.2269 | False | 219 |
| pooled vs zero_shot | seen | 64 | diebold_mariano | -4.9410 | 0.0000 | 0.0000 | True | 201 |
| pooled vs zero_shot | seen | 64 | diebold_mariano | -0.9491 | 0.3426 | 0.5775 | False | 210 |
| pooled vs zero_shot | seen | 64 | diebold_mariano | -0.7297 | 0.4656 | 0.7097 | False | 219 |
| pooled vs zero_shot | seen | 128 | diebold_mariano | -6.4122 | 0.0000 | 0.0000 | True | 201 |
| pooled vs zero_shot | seen | 128 | diebold_mariano | -3.0645 | 0.0022 | 0.0183 | True | 210 |
| pooled vs zero_shot | seen | 128 | diebold_mariano | -5.9668 | 0.0000 | 0.0000 | True | 219 |
