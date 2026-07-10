# Benchmark tables — sp500_2005-01-01_2026-01-01_f2026-06-04
_smoke=False_  ·  folds=3

## Table A — directional / trading (fold-mean)

| method | split | category | horizon | n_windows | n_trades | acc | always_up_acc | excess_acc | balanced_acc | mcc | sharpe | max_drawdown | hit_rate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| always_up | held_out | stock | 128 | 948 | 948 | 0.6581 | 0.6581 | 0.0000 | 0.5000 | 0.0000 | 0.4809 | -0.8062 | 0.6581 |
| always_up | held_out | stock | 16 | 948 | 948 | 0.5701 | 0.5701 | 0.0000 | 0.5000 | 0.0000 | 0.6742 | -0.4780 | 0.5701 |
| always_up | held_out | stock | 2 | 947 | 948 | 0.4746 | 0.4746 | 0.0000 | 0.5000 | 0.0000 | -0.5600 | -0.6091 | 0.4741 |
| always_up | held_out | stock | 32 | 947 | 948 | 0.6358 | 0.6358 | 0.0000 | 0.5000 | 0.0000 | 0.9614 | -0.5013 | 0.6352 |
| always_up | held_out | stock | 4 | 948 | 948 | 0.4910 | 0.4910 | 0.0000 | 0.5000 | 0.0000 | 0.4120 | -0.5194 | 0.4910 |
| always_up | held_out | stock | 64 | 948 | 948 | 0.5607 | 0.5607 | 0.0000 | 0.5000 | 0.0000 | 0.1135 | -0.9341 | 0.5607 |
| always_up | held_out | stock | 8 | 945 | 948 | 0.6112 | 0.6112 | 0.0000 | 0.5000 | 0.0000 | 1.8982 | -0.3309 | 0.6092 |
| always_up | seen | etf | 128 | 96 | 96 | 0.6798 | 0.6798 | 0.0000 | 0.5000 | 0.0000 | 0.7821 | -0.3007 | 0.6798 |
| always_up | seen | etf | 16 | 96 | 96 | 0.6030 | 0.6030 | 0.0000 | 0.5000 | 0.0000 | 0.9414 | -0.1381 | 0.6030 |
| always_up | seen | etf | 2 | 96 | 96 | 0.4707 | 0.4707 | 0.0000 | 0.5000 | 0.0000 | -0.4340 | -0.1000 | 0.4707 |
| always_up | seen | etf | 32 | 96 | 96 | 0.6687 | 0.6687 | 0.0000 | 0.5000 | 0.0000 | 1.5481 | -0.1297 | 0.6687 |
| always_up | seen | etf | 4 | 96 | 96 | 0.4707 | 0.4707 | 0.0000 | 0.5000 | 0.0000 | 0.3387 | -0.0940 | 0.4707 |
| always_up | seen | etf | 64 | 96 | 96 | 0.5242 | 0.5242 | 0.0000 | 0.5000 | 0.0000 | 0.1215 | -0.4490 | 0.5242 |
| always_up | seen | etf | 8 | 96 | 96 | 0.6788 | 0.6788 | 0.0000 | 0.5000 | 0.0000 | 2.7238 | -0.0643 | 0.6788 |
| always_up | seen | stock | 128 | 3423 | 3423 | 0.6275 | 0.6275 | 0.0000 | 0.5000 | 0.0000 | 0.4240 | -0.9240 | 0.6275 |
| always_up | seen | stock | 16 | 3423 | 3423 | 0.5974 | 0.5974 | 0.0000 | 0.5000 | 0.0000 | 0.7443 | -0.7955 | 0.5974 |
| always_up | seen | stock | 2 | 3421 | 3423 | 0.4562 | 0.4562 | 0.0000 | 0.5000 | 0.0000 | -0.8130 | -0.8215 | 0.4560 |
| always_up | seen | stock | 32 | 3422 | 3423 | 0.6368 | 0.6368 | 0.0000 | 0.5000 | 0.0000 | 0.8745 | -0.6730 | 0.6366 |
| always_up | seen | stock | 4 | 3422 | 3423 | 0.5040 | 0.5040 | 0.0000 | 0.5000 | 0.0000 | 0.3211 | -0.9538 | 0.5039 |
| always_up | seen | stock | 64 | 3423 | 3423 | 0.5338 | 0.5338 | 0.0000 | 0.5000 | 0.0000 | 0.0436 | -0.9980 | 0.5338 |
| always_up | seen | stock | 8 | 3418 | 3423 | 0.6331 | 0.6331 | 0.0000 | 0.5000 | 0.0000 | 1.8466 | -0.4781 | 0.6323 |
| ar1 | held_out | stock | 128 | 948 | 948 | 0.5649 | 0.6581 | -0.0932 | 0.4810 | -0.0514 | 0.1500 | -0.9316 | 0.5649 |
| ar1 | held_out | stock | 16 | 948 | 948 | 0.5447 | 0.5701 | -0.0254 | 0.5057 | 0.0058 | 0.2427 | -0.7297 | 0.5447 |
| ar1 | held_out | stock | 2 | 947 | 948 | 0.5050 | 0.4746 | 0.0304 | 0.5144 | 0.0279 | 0.4957 | -0.4683 | 0.5044 |
| ar1 | held_out | stock | 32 | 947 | 948 | 0.5540 | 0.6358 | -0.0818 | 0.4810 | -0.0507 | 0.3034 | -0.8464 | 0.5535 |
| ar1 | held_out | stock | 4 | 948 | 948 | 0.4785 | 0.4910 | -0.0125 | 0.4809 | -0.0494 | -0.1042 | -0.6229 | 0.4785 |
| ar1 | held_out | stock | 64 | 948 | 948 | 0.4943 | 0.5607 | -0.0664 | 0.4640 | -0.0908 | -0.0700 | -0.9953 | 0.4943 |
| ar1 | held_out | stock | 8 | 945 | 948 | 0.5292 | 0.6112 | -0.0820 | 0.4781 | -0.0570 | 0.4998 | -0.6966 | 0.5275 |
| ar1 | seen | etf | 128 | 96 | 96 | 0.5758 | 0.6798 | -0.1040 | 0.4584 | -0.1334 | 0.1580 | -0.5377 | 0.5758 |
| ar1 | seen | etf | 16 | 96 | 96 | 0.5929 | 0.6030 | -0.0101 | 0.5237 | 0.0364 | 0.8019 | -0.2186 | 0.5929 |
| ar1 | seen | etf | 2 | 96 | 96 | 0.4697 | 0.4707 | -0.0010 | 0.4987 | -0.0031 | -0.2832 | -0.0880 | 0.4697 |
| ar1 | seen | etf | 32 | 96 | 96 | 0.6071 | 0.6687 | -0.0616 | 0.5004 | -0.0299 | 0.8628 | -0.1964 | 0.6071 |
| ar1 | seen | etf | 4 | 96 | 96 | 0.4374 | 0.4707 | -0.0333 | 0.4630 | -0.0950 | 0.1164 | -0.1337 | 0.4374 |
| ar1 | seen | etf | 64 | 96 | 96 | 0.4424 | 0.5242 | -0.0818 | 0.4282 | -0.2139 | -0.1136 | -0.5509 | 0.4424 |
| ar1 | seen | etf | 8 | 96 | 96 | 0.6242 | 0.6788 | -0.0545 | 0.5301 | 0.0409 | 1.5084 | -0.1002 | 0.6242 |
| ar1 | seen | stock | 128 | 3423 | 3423 | 0.5637 | 0.6275 | -0.0637 | 0.4983 | -0.0112 | 0.1505 | -1.0000 | 0.5637 |
| ar1 | seen | stock | 16 | 3423 | 3423 | 0.5529 | 0.5974 | -0.0445 | 0.5016 | -0.0067 | 0.3259 | -0.8443 | 0.5529 |
| ar1 | seen | stock | 2 | 3421 | 3423 | 0.5172 | 0.4562 | 0.0610 | 0.5345 | 0.0667 | 0.8091 | -0.6777 | 0.5169 |
| ar1 | seen | stock | 32 | 3422 | 3423 | 0.5710 | 0.6368 | -0.0659 | 0.5006 | -0.0047 | 0.3729 | -0.9339 | 0.5708 |
| ar1 | seen | stock | 4 | 3422 | 3423 | 0.4969 | 0.5040 | -0.0071 | 0.4974 | -0.0144 | 0.0946 | -0.8432 | 0.4967 |
| ar1 | seen | stock | 64 | 3423 | 3423 | 0.5043 | 0.5338 | -0.0295 | 0.4913 | -0.0248 | -0.0342 | -1.0000 | 0.5043 |
| ar1 | seen | stock | 8 | 3418 | 3423 | 0.5473 | 0.6331 | -0.0858 | 0.4882 | -0.0403 | 0.5064 | -0.7125 | 0.5466 |
| per_sector | held_out | stock | 128 | 948 | 948 | 0.5993 | 0.6581 | -0.0588 | 0.5105 | 0.0268 | 0.2410 | -0.9819 | 0.5993 |
| per_sector | held_out | stock | 16 | 948 | 948 | 0.5709 | 0.5701 | 0.0008 | 0.5483 | 0.1085 | 0.4818 | -0.6764 | 0.5709 |
| per_sector | held_out | stock | 2 | 947 | 948 | 0.4437 | 0.4746 | -0.0309 | 0.4493 | -0.1163 | -1.1047 | -0.7282 | 0.4432 |
| per_sector | held_out | stock | 32 | 947 | 948 | 0.5904 | 0.6358 | -0.0455 | 0.5303 | 0.0703 | 0.6050 | -0.6727 | 0.5897 |
| per_sector | held_out | stock | 4 | 948 | 948 | 0.4553 | 0.4910 | -0.0357 | 0.4629 | -0.0973 | -0.1429 | -0.6054 | 0.4553 |
| per_sector | held_out | stock | 64 | 948 | 948 | 0.5165 | 0.5607 | -0.0442 | 0.4936 | -0.0138 | 0.0072 | -0.9631 | 0.5165 |
| per_sector | held_out | stock | 8 | 945 | 948 | 0.5717 | 0.6112 | -0.0395 | 0.5363 | 0.0797 | 0.9329 | -0.4495 | 0.5699 |
| per_sector | seen | etf | 128 | 96 | 96 | 0.6091 | 0.6798 | -0.0707 | 0.4696 | -0.0367 | 0.5037 | -0.3415 | 0.6091 |
| per_sector | seen | etf | 16 | 96 | 96 | 0.5424 | 0.6030 | -0.0606 | 0.4913 | -0.0056 | 0.5200 | -0.2151 | 0.5424 |
| per_sector | seen | etf | 2 | 96 | 96 | 0.4778 | 0.4707 | 0.0071 | 0.4741 | -0.0741 | -0.3654 | -0.1128 | 0.4778 |
| per_sector | seen | etf | 32 | 96 | 96 | 0.6354 | 0.6687 | -0.0333 | 0.5413 | 0.1107 | 0.9015 | -0.1425 | 0.6354 |
| per_sector | seen | etf | 4 | 96 | 96 | 0.4586 | 0.4707 | -0.0121 | 0.4820 | -0.0494 | 0.2079 | -0.0830 | 0.4586 |
| per_sector | seen | etf | 64 | 96 | 96 | 0.5020 | 0.5242 | -0.0222 | 0.4973 | -0.0234 | 0.0919 | -0.4713 | 0.5020 |
| per_sector | seen | etf | 8 | 96 | 96 | 0.5455 | 0.6788 | -0.1333 | 0.4758 | -0.0411 | 1.0778 | -0.1007 | 0.5455 |
| per_sector | seen | stock | 128 | 3423 | 3423 | 0.5611 | 0.6275 | -0.0664 | 0.4860 | -0.0361 | 0.2360 | -1.0000 | 0.5611 |
| per_sector | seen | stock | 16 | 3423 | 3423 | 0.5656 | 0.5974 | -0.0318 | 0.5259 | 0.0617 | 0.5124 | -0.9261 | 0.5656 |
| per_sector | seen | stock | 2 | 3421 | 3423 | 0.4696 | 0.4562 | 0.0134 | 0.4760 | -0.0591 | -0.5247 | -0.9509 | 0.4693 |
| per_sector | seen | stock | 32 | 3422 | 3423 | 0.5767 | 0.6368 | -0.0602 | 0.5150 | 0.0347 | 0.4748 | -0.9578 | 0.5765 |
| per_sector | seen | stock | 4 | 3422 | 3423 | 0.4750 | 0.5040 | -0.0290 | 0.4746 | -0.0687 | -0.2481 | -0.9398 | 0.4748 |
| per_sector | seen | stock | 64 | 3423 | 3423 | 0.4912 | 0.5338 | -0.0426 | 0.4787 | -0.0540 | -0.0520 | -1.0000 | 0.4912 |
| per_sector | seen | stock | 8 | 3418 | 3423 | 0.5661 | 0.6331 | -0.0671 | 0.5224 | 0.0502 | 0.8862 | -0.6918 | 0.5652 |
| persistence | held_out | stock | 128 | 936 | 936 | 0.5379 | 0.6594 | -0.1215 | 0.5057 | 0.0111 | 0.1679 | -0.9445 | 0.5379 |
| persistence | held_out | stock | 16 | 936 | 936 | 0.5375 | 0.5732 | -0.0357 | 0.5407 | 0.0864 | 0.3034 | -0.7116 | 0.5375 |
| persistence | held_out | stock | 2 | 935 | 936 | 0.4820 | 0.4740 | 0.0080 | 0.4766 | -0.0525 | -0.3176 | -0.5682 | 0.4815 |
| persistence | held_out | stock | 32 | 935 | 936 | 0.5609 | 0.6408 | -0.0800 | 0.5316 | 0.0651 | 0.4392 | -0.7100 | 0.5603 |
| persistence | held_out | stock | 4 | 936 | 936 | 0.4827 | 0.4911 | -0.0084 | 0.4978 | -0.0064 | 0.0284 | -0.5332 | 0.4827 |
| persistence | held_out | stock | 64 | 936 | 936 | 0.5311 | 0.5629 | -0.0318 | 0.5295 | 0.0597 | 0.0234 | -0.9895 | 0.5311 |
| persistence | held_out | stock | 8 | 933 | 936 | 0.5608 | 0.6129 | -0.0521 | 0.5542 | 0.1106 | 0.5603 | -0.5421 | 0.5590 |
| persistence | seen | etf | 128 | 96 | 96 | 0.5465 | 0.6798 | -0.1333 | 0.5039 | 0.0219 | 0.1502 | -0.5784 | 0.5465 |
| persistence | seen | etf | 16 | 96 | 96 | 0.4879 | 0.6030 | -0.1152 | 0.4738 | -0.0874 | 0.1977 | -0.2835 | 0.4879 |
| persistence | seen | etf | 2 | 96 | 96 | 0.5172 | 0.4707 | 0.0465 | 0.4992 | -0.0476 | 0.7650 | -0.0952 | 0.5172 |
| persistence | seen | etf | 32 | 96 | 96 | 0.5737 | 0.6687 | -0.0949 | 0.5285 | 0.0414 | 0.6512 | -0.2561 | 0.5737 |
| persistence | seen | etf | 4 | 96 | 96 | 0.4788 | 0.4707 | 0.0081 | 0.4776 | -0.0618 | 0.4833 | -0.1206 | 0.4788 |
| persistence | seen | etf | 64 | 96 | 96 | 0.5323 | 0.5242 | 0.0081 | 0.5338 | 0.0569 | 0.0880 | -0.4867 | 0.5323 |
| persistence | seen | etf | 8 | 96 | 96 | 0.5838 | 0.6788 | -0.0949 | 0.5416 | 0.0623 | 0.7500 | -0.1457 | 0.5838 |
| persistence | seen | stock | 128 | 3406 | 3406 | 0.5589 | 0.6272 | -0.0684 | 0.5245 | 0.0515 | 0.1726 | -1.0000 | 0.5589 |
| persistence | seen | stock | 16 | 3406 | 3406 | 0.5264 | 0.5974 | -0.0709 | 0.5184 | 0.0348 | 0.1668 | -0.9869 | 0.5264 |
| persistence | seen | stock | 2 | 3404 | 3406 | 0.4922 | 0.4564 | 0.0358 | 0.4777 | -0.0542 | 0.3171 | -0.7055 | 0.4919 |
| persistence | seen | stock | 32 | 3405 | 3406 | 0.5604 | 0.6371 | -0.0768 | 0.5306 | 0.0631 | 0.4331 | -0.8585 | 0.5602 |
| persistence | seen | stock | 4 | 3405 | 3406 | 0.4893 | 0.5033 | -0.0141 | 0.4976 | -0.0069 | 0.2276 | -0.8432 | 0.4891 |
| persistence | seen | stock | 64 | 3406 | 3406 | 0.5269 | 0.5340 | -0.0071 | 0.5277 | 0.0601 | 0.0618 | -1.0000 | 0.5269 |
| persistence | seen | stock | 8 | 3401 | 3406 | 0.5513 | 0.6340 | -0.0827 | 0.5342 | 0.0673 | 0.5259 | -0.7566 | 0.5505 |
| pooled | held_out | stock | 128 | 948 | 948 | 0.6413 | 0.6581 | -0.0167 | 0.4944 | -0.0360 | 0.4452 | -0.8280 | 0.6413 |
| pooled | held_out | stock | 16 | 948 | 948 | 0.5895 | 0.5701 | 0.0194 | 0.5430 | 0.1279 | 0.8091 | -0.5856 | 0.5895 |
| pooled | held_out | stock | 2 | 947 | 948 | 0.4788 | 0.4746 | 0.0042 | 0.5045 | 0.0030 | -0.7672 | -0.6520 | 0.4783 |
| pooled | held_out | stock | 32 | 947 | 948 | 0.6308 | 0.6358 | -0.0050 | 0.5196 | 0.0605 | 0.9061 | -0.5369 | 0.6301 |
| pooled | held_out | stock | 4 | 948 | 948 | 0.4825 | 0.4910 | -0.0085 | 0.4904 | -0.0423 | 0.2215 | -0.5730 | 0.4825 |
| pooled | held_out | stock | 64 | 948 | 948 | 0.5439 | 0.5607 | -0.0168 | 0.4964 | -0.0198 | 0.0823 | -0.9593 | 0.5439 |
| pooled | held_out | stock | 8 | 945 | 948 | 0.6135 | 0.6112 | 0.0023 | 0.5389 | 0.1073 | 1.6469 | -0.3264 | 0.6115 |
| pooled | seen | etf | 128 | 96 | 96 | 0.6495 | 0.6798 | -0.0303 | 0.4815 | -0.0497 | 0.6144 | -0.3215 | 0.6495 |
| pooled | seen | etf | 16 | 96 | 96 | 0.6253 | 0.6030 | 0.0222 | 0.5522 | 0.2046 | 1.3104 | -0.1326 | 0.6253 |
| pooled | seen | etf | 2 | 96 | 96 | 0.4687 | 0.4707 | -0.0020 | 0.4940 | -0.0422 | -0.1472 | -0.0907 | 0.4687 |
| pooled | seen | etf | 32 | 96 | 96 | 0.6899 | 0.6687 | 0.0212 | 0.5667 | 0.2474 | 1.4000 | -0.1393 | 0.6899 |
| pooled | seen | etf | 4 | 96 | 96 | 0.4586 | 0.4707 | -0.0121 | 0.4853 | -0.0982 | 0.1170 | -0.1008 | 0.4586 |
| pooled | seen | etf | 64 | 96 | 96 | 0.5141 | 0.5242 | -0.0101 | 0.5159 | 0.0343 | 0.0600 | -0.4912 | 0.5141 |
| pooled | seen | etf | 8 | 96 | 96 | 0.6596 | 0.6788 | -0.0192 | 0.5298 | 0.1317 | 2.3610 | -0.0630 | 0.6596 |
| pooled | seen | stock | 128 | 3423 | 3423 | 0.6148 | 0.6275 | -0.0127 | 0.4954 | -0.0150 | 0.3970 | -0.9176 | 0.6148 |
| pooled | seen | stock | 16 | 3423 | 3423 | 0.5970 | 0.5974 | -0.0004 | 0.5263 | 0.0881 | 0.7494 | -0.7023 | 0.5970 |
| pooled | seen | stock | 2 | 3421 | 3423 | 0.4466 | 0.4562 | -0.0096 | 0.4872 | -0.0465 | -0.8442 | -0.8233 | 0.4464 |
| pooled | seen | stock | 32 | 3422 | 3423 | 0.6288 | 0.6368 | -0.0080 | 0.5136 | 0.0504 | 0.8402 | -0.6499 | 0.6287 |
| pooled | seen | stock | 4 | 3422 | 3423 | 0.4969 | 0.5040 | -0.0072 | 0.4940 | -0.0305 | 0.2462 | -0.9339 | 0.4967 |
| pooled | seen | stock | 64 | 3423 | 3423 | 0.5153 | 0.5338 | -0.0185 | 0.4897 | -0.0444 | -0.0047 | -0.9964 | 0.5153 |
| pooled | seen | stock | 8 | 3418 | 3423 | 0.6188 | 0.6331 | -0.0144 | 0.5237 | 0.0708 | 1.5845 | -0.5400 | 0.6179 |
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
| zero_shot | held_out | stock | 128 | 948 | 948 | 0.5328 | 0.6581 | -0.1253 | 0.5050 | 0.0099 | 0.1220 | -0.9985 | 0.5328 |
| zero_shot | held_out | stock | 16 | 948 | 948 | 0.5422 | 0.5701 | -0.0279 | 0.5252 | 0.0520 | 0.3682 | -0.7525 | 0.5422 |
| zero_shot | held_out | stock | 2 | 947 | 948 | 0.4510 | 0.4746 | -0.0236 | 0.4605 | -0.0947 | -1.0387 | -0.6261 | 0.4506 |
| zero_shot | held_out | stock | 32 | 947 | 948 | 0.5556 | 0.6358 | -0.0802 | 0.5244 | 0.0498 | 0.3417 | -0.8026 | 0.5550 |
| zero_shot | held_out | stock | 4 | 948 | 948 | 0.4688 | 0.4910 | -0.0222 | 0.4746 | -0.0621 | 0.1232 | -0.5084 | 0.4688 |
| zero_shot | held_out | stock | 64 | 948 | 948 | 0.5020 | 0.5607 | -0.0587 | 0.4906 | -0.0186 | 0.0545 | -0.9760 | 0.5020 |
| zero_shot | held_out | stock | 8 | 945 | 948 | 0.5368 | 0.6112 | -0.0744 | 0.5163 | 0.0336 | 0.6753 | -0.4900 | 0.5351 |
| zero_shot | seen | etf | 128 | 96 | 96 | 0.5545 | 0.6798 | -0.1253 | 0.5535 | 0.0787 | 0.0701 | -0.6071 | 0.5545 |
| zero_shot | seen | etf | 16 | 96 | 96 | 0.5758 | 0.6030 | -0.0273 | 0.5562 | 0.1208 | 0.8559 | -0.1804 | 0.5758 |
| zero_shot | seen | etf | 2 | 96 | 96 | 0.4636 | 0.4707 | -0.0071 | 0.4616 | -0.1470 | -0.0484 | -0.0815 | 0.4636 |
| zero_shot | seen | etf | 32 | 96 | 96 | 0.6020 | 0.6687 | -0.0667 | 0.5812 | 0.1591 | 0.4369 | -0.2412 | 0.6020 |
| zero_shot | seen | etf | 4 | 96 | 96 | 0.4465 | 0.4707 | -0.0242 | 0.4671 | -0.0848 | -0.0994 | -0.1383 | 0.4465 |
| zero_shot | seen | etf | 64 | 96 | 96 | 0.5202 | 0.5242 | -0.0040 | 0.5168 | 0.0331 | 0.0674 | -0.4661 | 0.5202 |
| zero_shot | seen | etf | 8 | 96 | 96 | 0.5646 | 0.6788 | -0.1141 | 0.5185 | 0.0417 | 0.9829 | -0.0985 | 0.5646 |
| zero_shot | seen | stock | 128 | 3423 | 3423 | 0.5113 | 0.6275 | -0.1161 | 0.4970 | -0.0072 | 0.0651 | -1.0000 | 0.5113 |
| zero_shot | seen | stock | 16 | 3423 | 3423 | 0.5326 | 0.5974 | -0.0648 | 0.5071 | 0.0146 | 0.2316 | -0.8353 | 0.5326 |
| zero_shot | seen | stock | 2 | 3421 | 3423 | 0.4411 | 0.4562 | -0.0151 | 0.4598 | -0.0990 | -0.8915 | -0.9286 | 0.4408 |
| zero_shot | seen | stock | 32 | 3422 | 3423 | 0.5082 | 0.6368 | -0.1286 | 0.4802 | -0.0389 | 0.0690 | -0.9995 | 0.5080 |
| zero_shot | seen | stock | 4 | 3422 | 3423 | 0.4676 | 0.5040 | -0.0365 | 0.4659 | -0.0813 | -0.4980 | -0.9286 | 0.4674 |
| zero_shot | seen | stock | 64 | 3423 | 3423 | 0.4761 | 0.5338 | -0.0577 | 0.4706 | -0.0592 | -0.0920 | -1.0000 | 0.4761 |
| zero_shot | seen | stock | 8 | 3418 | 3423 | 0.5258 | 0.6331 | -0.1073 | 0.4998 | -0.0021 | 0.3600 | -0.7781 | 0.5251 |

## Table B — point forecast (fold-mean, macro-averaged)

| method | split | category | n_windows | MAE | RMSE | sMAPE | MASE |
|---|---|---|---|---|---|---|---|
| always_up | held_out | stock | 948 | 15.5551 | 19.6384 | 0.1240 | 25.7894 |
| always_up | seen | etf | 96 | 4.5237 | 5.6286 | 0.0828 | 20.5053 |
| always_up | seen | stock | 3423 | 18.7141 | 23.6284 | 0.1246 | 27.3687 |
| ar1 | held_out | stock | 948 | 15.9922 | 20.8650 | 0.1278 | 26.7594 |
| ar1 | seen | etf | 96 | 4.8491 | 6.1772 | 0.0855 | 21.5071 |
| ar1 | seen | stock | 3423 | 19.8558 | 25.6029 | 0.1294 | 29.5486 |
| per_sector | held_out | stock | 948 | 15.5468 | 19.7846 | 0.1243 | 26.0212 |
| per_sector | seen | etf | 96 | 4.5455 | 5.6433 | 0.0824 | 20.4024 |
| per_sector | seen | stock | 3423 | 19.1511 | 24.4279 | 0.1262 | 28.0608 |
| pooled | held_out | stock | 948 | 15.1536 | 19.3724 | 0.1197 | 25.0790 |
| pooled | seen | etf | 96 | 4.4021 | 5.5031 | 0.0797 | 19.6542 |
| pooled | seen | stock | 3423 | 18.5699 | 23.5909 | 0.1219 | 26.9805 |
| random_walk | held_out | stock | 948 | 15.5567 | 19.6399 | 0.1240 | 25.7914 |
| random_walk | seen | etf | 96 | 4.5241 | 5.6291 | 0.0828 | 20.5073 |
| random_walk | seen | stock | 3423 | 18.7151 | 23.6295 | 0.1246 | 27.3703 |
| zero_shot | held_out | stock | 948 | 16.3145 | 20.6938 | 0.1294 | 26.9024 |
| zero_shot | seen | etf | 96 | 4.6498 | 5.8082 | 0.0851 | 21.0324 |
| zero_shot | seen | stock | 3423 | 19.7793 | 25.1282 | 0.1309 | 29.0078 |

## Table C — calibration (fold-mean)

| method | split | category | quantile_level | nominal | empirical_coverage | pinball |
|---|---|---|---|---|---|---|
| per_sector | held_out | stock | 0.0500 | 0.0500 | 0.4380 | 6.5994 |
| per_sector | held_out | stock | 0.1000 | 0.1000 | 0.1633 | 3.8896 |
| per_sector | held_out | stock | 0.2000 | 0.2000 | 0.2479 | 5.8666 |
| per_sector | held_out | stock | 0.3000 | 0.3000 | 0.3218 | 7.0209 |
| per_sector | held_out | stock | 0.4000 | 0.4000 | 0.3919 | 7.6209 |
| per_sector | held_out | stock | 0.5000 | 0.5000 | 0.4626 | 7.7734 |
| per_sector | held_out | stock | 0.6000 | 0.6000 | 0.5338 | 7.5320 |
| per_sector | held_out | stock | 0.7000 | 0.7000 | 0.6125 | 6.8942 |
| per_sector | held_out | stock | 0.8000 | 0.8000 | 0.6937 | 5.8165 |
| per_sector | held_out | stock | 0.9000 | 0.9000 | 0.7914 | 4.0483 |
| per_sector | seen | etf | 0.0500 | 0.0500 | 0.4207 | 1.9697 |
| per_sector | seen | etf | 0.1000 | 0.1000 | 0.1662 | 1.3162 |
| per_sector | seen | etf | 0.2000 | 0.2000 | 0.2396 | 1.8189 |
| per_sector | seen | etf | 0.3000 | 0.3000 | 0.3142 | 2.0909 |
| per_sector | seen | etf | 0.4000 | 0.4000 | 0.3887 | 2.2354 |
| per_sector | seen | etf | 0.5000 | 0.5000 | 0.4493 | 2.2727 |
| per_sector | seen | etf | 0.6000 | 0.6000 | 0.5072 | 2.1852 |
| per_sector | seen | etf | 0.7000 | 0.7000 | 0.5774 | 1.9678 |
| per_sector | seen | etf | 0.8000 | 0.8000 | 0.6577 | 1.6169 |
| per_sector | seen | etf | 0.9000 | 0.9000 | 0.7705 | 1.0861 |
| per_sector | seen | stock | 0.0500 | 0.0500 | 0.4522 | 8.9367 |
| per_sector | seen | stock | 0.1000 | 0.1000 | 0.1626 | 5.1689 |
| per_sector | seen | stock | 0.2000 | 0.2000 | 0.2506 | 7.3668 |
| per_sector | seen | stock | 0.3000 | 0.3000 | 0.3281 | 8.6646 |
| per_sector | seen | stock | 0.4000 | 0.4000 | 0.4032 | 9.3694 |
| per_sector | seen | stock | 0.5000 | 0.5000 | 0.4783 | 9.5755 |
| per_sector | seen | stock | 0.6000 | 0.6000 | 0.5510 | 9.2839 |
| per_sector | seen | stock | 0.7000 | 0.7000 | 0.6261 | 8.4690 |
| per_sector | seen | stock | 0.8000 | 0.8000 | 0.7069 | 7.0461 |
| per_sector | seen | stock | 0.9000 | 0.9000 | 0.8031 | 4.7542 |
| pooled | held_out | stock | 0.0500 | 0.0500 | 0.4399 | 6.5276 |
| pooled | held_out | stock | 0.1000 | 0.1000 | 0.1521 | 3.9604 |
| pooled | held_out | stock | 0.2000 | 0.2000 | 0.2389 | 5.8132 |
| pooled | held_out | stock | 0.3000 | 0.3000 | 0.3140 | 6.8939 |
| pooled | held_out | stock | 0.4000 | 0.4000 | 0.3924 | 7.4489 |
| pooled | held_out | stock | 0.5000 | 0.5000 | 0.4715 | 7.5768 |
| pooled | held_out | stock | 0.6000 | 0.6000 | 0.5532 | 7.3046 |
| pooled | held_out | stock | 0.7000 | 0.7000 | 0.6350 | 6.6428 |
| pooled | held_out | stock | 0.8000 | 0.8000 | 0.7148 | 5.5206 |
| pooled | held_out | stock | 0.9000 | 0.9000 | 0.8075 | 3.7399 |
| pooled | seen | etf | 0.0500 | 0.0500 | 0.4019 | 1.9092 |
| pooled | seen | etf | 0.1000 | 0.1000 | 0.1476 | 1.3190 |
| pooled | seen | etf | 0.2000 | 0.2000 | 0.2171 | 1.7656 |
| pooled | seen | etf | 0.3000 | 0.3000 | 0.2978 | 2.0250 |
| pooled | seen | etf | 0.4000 | 0.4000 | 0.3721 | 2.1714 |
| pooled | seen | etf | 0.5000 | 0.5000 | 0.4449 | 2.2010 |
| pooled | seen | etf | 0.6000 | 0.6000 | 0.5117 | 2.1073 |
| pooled | seen | etf | 0.7000 | 0.7000 | 0.5863 | 1.8855 |
| pooled | seen | etf | 0.8000 | 0.8000 | 0.6746 | 1.5261 |
| pooled | seen | etf | 0.9000 | 0.9000 | 0.7897 | 1.0051 |
| pooled | seen | stock | 0.0500 | 0.0500 | 0.4556 | 8.6726 |
| pooled | seen | stock | 0.1000 | 0.1000 | 0.1514 | 5.0101 |
| pooled | seen | stock | 0.2000 | 0.2000 | 0.2401 | 7.1107 |
| pooled | seen | stock | 0.3000 | 0.3000 | 0.3253 | 8.3703 |
| pooled | seen | stock | 0.4000 | 0.4000 | 0.4077 | 9.0818 |
| pooled | seen | stock | 0.5000 | 0.5000 | 0.4875 | 9.2849 |
| pooled | seen | stock | 0.6000 | 0.6000 | 0.5636 | 8.9741 |
| pooled | seen | stock | 0.7000 | 0.7000 | 0.6416 | 8.1208 |
| pooled | seen | stock | 0.8000 | 0.8000 | 0.7246 | 6.6630 |
| pooled | seen | stock | 0.9000 | 0.9000 | 0.8217 | 4.3852 |
| zero_shot | held_out | stock | 0.0500 | 0.0500 | 0.4084 | 6.3767 |
| zero_shot | held_out | stock | 0.1000 | 0.1000 | 0.1372 | 3.8937 |
| zero_shot | held_out | stock | 0.2000 | 0.2000 | 0.2184 | 6.0063 |
| zero_shot | held_out | stock | 0.3000 | 0.3000 | 0.2922 | 7.2819 |
| zero_shot | held_out | stock | 0.4000 | 0.4000 | 0.3625 | 7.9616 |
| zero_shot | held_out | stock | 0.5000 | 0.5000 | 0.4340 | 8.1572 |
| zero_shot | held_out | stock | 0.6000 | 0.6000 | 0.5085 | 7.9034 |
| zero_shot | held_out | stock | 0.7000 | 0.7000 | 0.5919 | 7.2010 |
| zero_shot | held_out | stock | 0.8000 | 0.8000 | 0.6852 | 6.0179 |
| zero_shot | held_out | stock | 0.9000 | 0.9000 | 0.7943 | 4.0905 |
| zero_shot | seen | etf | 0.0500 | 0.0500 | 0.3895 | 1.8300 |
| zero_shot | seen | etf | 0.1000 | 0.1000 | 0.1479 | 1.2536 |
| zero_shot | seen | etf | 0.2000 | 0.2000 | 0.2139 | 1.8143 |
| zero_shot | seen | etf | 0.3000 | 0.3000 | 0.2800 | 2.1104 |
| zero_shot | seen | etf | 0.4000 | 0.4000 | 0.3528 | 2.2688 |
| zero_shot | seen | etf | 0.5000 | 0.5000 | 0.4286 | 2.3249 |
| zero_shot | seen | etf | 0.6000 | 0.6000 | 0.4946 | 2.2706 |
| zero_shot | seen | etf | 0.7000 | 0.7000 | 0.5619 | 2.0650 |
| zero_shot | seen | etf | 0.8000 | 0.8000 | 0.6524 | 1.6950 |
| zero_shot | seen | etf | 0.9000 | 0.9000 | 0.7716 | 1.1583 |
| zero_shot | seen | stock | 0.0500 | 0.0500 | 0.4166 | 8.2279 |
| zero_shot | seen | stock | 0.1000 | 0.1000 | 0.1363 | 4.8857 |
| zero_shot | seen | stock | 0.2000 | 0.2000 | 0.2170 | 7.2883 |
| zero_shot | seen | stock | 0.3000 | 0.3000 | 0.2929 | 8.7345 |
| zero_shot | seen | stock | 0.4000 | 0.4000 | 0.3686 | 9.5829 |
| zero_shot | seen | stock | 0.5000 | 0.5000 | 0.4436 | 9.8897 |
| zero_shot | seen | stock | 0.6000 | 0.6000 | 0.5195 | 9.6624 |
| zero_shot | seen | stock | 0.7000 | 0.7000 | 0.5994 | 8.8612 |
| zero_shot | seen | stock | 0.8000 | 0.8000 | 0.6890 | 7.4009 |
| zero_shot | seen | stock | 0.9000 | 0.9000 | 0.7970 | 5.0428 |

## Table D — significance (primary test flagged ★)

| comparison | split | horizon | test | statistic | p | fdr_adjusted | fdr_reject | n |
|---|---|---|---|---|---|---|---|---|
| ★ per_sector vs pooled | held_out | 128 | diebold_mariano | 5.1211 | 0.0000 |  |  | 312 |
| ★ per_sector vs pooled | held_out | 128 | diebold_mariano | 1.0333 | 0.3015 |  |  | 315 |
| ★ per_sector vs pooled | held_out | 128 | diebold_mariano | 5.5013 | 0.0000 |  |  | 321 |
| per_sector vs always_up | held_out | 2 | mcnemar | 1.2075 | 0.2717 | 0.3652 | False | 53 |
| per_sector vs always_up | held_out | 2 | mcnemar | 6.9605 | 0.0079 | 0.0218 | True | 76 |
| per_sector vs always_up | held_out | 2 | mcnemar | 0.0789 | 0.7789 | 0.8715 | False | 114 |
| per_sector vs always_up | held_out | 4 | mcnemar | 0.3404 | 0.5601 | 0.6820 | False | 47 |
| per_sector vs always_up | held_out | 4 | mcnemar | 1.8182 | 0.1770 | 0.2543 | False | 55 |
| per_sector vs always_up | held_out | 4 | mcnemar | 4.3788 | 0.0356 | 0.0708 | False | 66 |
| per_sector vs always_up | held_out | 8 | mcnemar | 0.0000 | 1.0000 | 1.0000 | False | 81 |
| per_sector vs always_up | held_out | 8 | mcnemar | 0.1758 | 0.6752 | 0.7852 | False | 91 |
| per_sector vs always_up | held_out | 8 | mcnemar | 14.9113 | 0.0001 | 0.0006 | True | 124 |
| per_sector vs always_up | held_out | 16 | mcnemar | 6.0114 | 0.0138 | 0.0353 | True | 88 |
| per_sector vs always_up | held_out | 16 | mcnemar | 0.1250 | 0.7239 | 0.8230 | False | 72 |
| per_sector vs always_up | held_out | 16 | mcnemar | 5.5227 | 0.0184 | 0.0433 | True | 132 |
| per_sector vs always_up | held_out | 32 | mcnemar | 12.9643 | 0.0003 | 0.0012 | True | 84 |
| per_sector vs always_up | held_out | 32 | mcnemar | 0.9552 | 0.3284 | 0.4261 | False | 67 |
| per_sector vs always_up | held_out | 32 | mcnemar | 2.7264 | 0.0982 | 0.1614 | False | 106 |
| per_sector vs always_up | held_out | 64 | mcnemar | 5.5125 | 0.0183 | 0.0433 | True | 80 |
| per_sector vs always_up | held_out | 64 | mcnemar | 0.2045 | 0.6516 | 0.7752 | False | 44 |
| per_sector vs always_up | held_out | 64 | mcnemar | 5.2900 | 0.0210 | 0.0477 | True | 100 |
| per_sector vs always_up | held_out | 128 | mcnemar | 6.8906 | 0.0081 | 0.0219 | True | 64 |
| per_sector vs always_up | held_out | 128 | mcnemar | 0.0000 | 1.0000 | 1.0000 | False | 43 |
| per_sector vs always_up | held_out | 128 | mcnemar | 12.6420 | 0.0003 | 0.0013 | True | 81 |
| per_sector vs pooled | held_out | 2 | diebold_mariano | -2.0694 | 0.0385 | 0.0752 | False | 312 |
| per_sector vs pooled | held_out | 2 | diebold_mariano | -1.3350 | 0.1819 | 0.2561 | False | 315 |
| per_sector vs pooled | held_out | 2 | diebold_mariano | -0.8639 | 0.3876 | 0.4834 | False | 321 |
| per_sector vs pooled | held_out | 4 | diebold_mariano | 2.1351 | 0.0328 | 0.0665 | False | 312 |
| per_sector vs pooled | held_out | 4 | diebold_mariano | -0.4035 | 0.6866 | 0.7933 | False | 315 |
| per_sector vs pooled | held_out | 4 | diebold_mariano | 2.6850 | 0.0073 | 0.0209 | True | 321 |
| per_sector vs pooled | held_out | 8 | diebold_mariano | 3.2573 | 0.0011 | 0.0039 | True | 312 |
| per_sector vs pooled | held_out | 8 | diebold_mariano | 2.1513 | 0.0315 | 0.0645 | False | 315 |
| per_sector vs pooled | held_out | 8 | diebold_mariano | 3.5693 | 0.0004 | 0.0015 | True | 321 |
| per_sector vs pooled | held_out | 16 | diebold_mariano | 1.4299 | 0.1527 | 0.2259 | False | 312 |
| per_sector vs pooled | held_out | 16 | diebold_mariano | 0.7930 | 0.4278 | 0.5271 | False | 315 |
| per_sector vs pooled | held_out | 16 | diebold_mariano | 2.4050 | 0.0162 | 0.0389 | True | 321 |
| per_sector vs pooled | held_out | 32 | diebold_mariano | 3.4294 | 0.0006 | 0.0023 | True | 312 |
| per_sector vs pooled | held_out | 32 | diebold_mariano | 1.2807 | 0.2003 | 0.2801 | False | 315 |
| per_sector vs pooled | held_out | 32 | diebold_mariano | 2.2011 | 0.0277 | 0.0580 | False | 321 |
| per_sector vs pooled | held_out | 64 | diebold_mariano | 0.5348 | 0.5928 | 0.7176 | False | 312 |
| per_sector vs pooled | held_out | 64 | diebold_mariano | 1.4739 | 0.1405 | 0.2108 | False | 315 |
| per_sector vs pooled | held_out | 64 | diebold_mariano | 2.2368 | 0.0253 | 0.0540 | False | 321 |
| per_sector vs zero_shot | held_out | 2 | diebold_mariano | 1.6754 | 0.0939 | 0.1606 | False | 312 |
| per_sector vs zero_shot | held_out | 2 | diebold_mariano | 1.6633 | 0.0963 | 0.1606 | False | 315 |
| per_sector vs zero_shot | held_out | 2 | diebold_mariano | 1.6402 | 0.1010 | 0.1645 | False | 321 |
| per_sector vs zero_shot | held_out | 4 | diebold_mariano | 0.9959 | 0.3193 | 0.4183 | False | 312 |
| per_sector vs zero_shot | held_out | 4 | diebold_mariano | 2.3104 | 0.0209 | 0.0477 | True | 315 |
| per_sector vs zero_shot | held_out | 4 | diebold_mariano | 1.8523 | 0.0640 | 0.1160 | False | 321 |
| per_sector vs zero_shot | held_out | 8 | diebold_mariano | 0.0411 | 0.9672 | 1.0000 | False | 312 |
| per_sector vs zero_shot | held_out | 8 | diebold_mariano | 0.0912 | 0.9273 | 0.9849 | False | 315 |
| per_sector vs zero_shot | held_out | 8 | diebold_mariano | -0.8121 | 0.4167 | 0.5165 | False | 321 |
| per_sector vs zero_shot | held_out | 16 | diebold_mariano | -0.4387 | 0.6609 | 0.7805 | False | 312 |
| per_sector vs zero_shot | held_out | 16 | diebold_mariano | -1.1699 | 0.2421 | 0.3318 | False | 315 |
| per_sector vs zero_shot | held_out | 16 | diebold_mariano | 0.3484 | 0.7275 | 0.8230 | False | 321 |
| per_sector vs zero_shot | held_out | 32 | diebold_mariano | -1.0057 | 0.3146 | 0.4147 | False | 312 |
| per_sector vs zero_shot | held_out | 32 | diebold_mariano | -0.1910 | 0.8485 | 0.9293 | False | 315 |
| per_sector vs zero_shot | held_out | 32 | diebold_mariano | -1.3465 | 0.1781 | 0.2543 | False | 321 |
| per_sector vs zero_shot | held_out | 64 | diebold_mariano | -1.9806 | 0.0476 | 0.0880 | False | 312 |
| per_sector vs zero_shot | held_out | 64 | diebold_mariano | 0.8939 | 0.3714 | 0.4716 | False | 315 |
| per_sector vs zero_shot | held_out | 64 | diebold_mariano | -2.2912 | 0.0219 | 0.0483 | True | 321 |
| per_sector vs zero_shot | held_out | 128 | diebold_mariano | -7.1233 | 0.0000 | 0.0000 | True | 312 |
| per_sector vs zero_shot | held_out | 128 | diebold_mariano | -0.4296 | 0.6675 | 0.7806 | False | 315 |
| per_sector vs zero_shot | held_out | 128 | diebold_mariano | -4.4246 | 0.0000 | 0.0001 | True | 321 |
| pooled vs always_up | held_out | 2 | mcnemar | 0.1905 | 0.6636 | 0.7805 | False | 21 |
| pooled vs always_up | held_out | 2 | mcnemar | 0.5208 | 0.4709 | 0.5768 | False | 48 |
| pooled vs always_up | held_out | 2 | mcnemar | 0.0000 | 1.0000 | 1.0000 | False | 17 |
| pooled vs always_up | held_out | 4 | mcnemar | 1.5625 | 0.2101 | 0.2919 | False | 16 |
| pooled vs always_up | held_out | 4 | mcnemar | 0.0000 | 1.0000 | 1.0000 | False | 21 |
| pooled vs always_up | held_out | 4 | mcnemar | 0.0000 | 1.0000 | 1.0000 | False | 19 |
| pooled vs always_up | held_out | 8 | mcnemar | 0.0333 | 1.0000 | 1.0000 | False | 30 |
| pooled vs always_up | held_out | 8 | mcnemar | 2.7500 | 0.0961 | 0.1606 | False | 44 |
| pooled vs always_up | held_out | 8 | mcnemar | 1.3500 | 0.2451 | 0.3337 | False | 60 |
| pooled vs always_up | held_out | 16 | mcnemar | 4.9655 | 0.0241 | 0.0520 | False | 29 |
| pooled vs always_up | held_out | 16 | mcnemar | 5.4468 | 0.0186 | 0.0433 | True | 47 |
| pooled vs always_up | held_out | 16 | mcnemar | 2.2407 | 0.1337 | 0.2020 | False | 54 |
| pooled vs always_up | held_out | 32 | mcnemar | 2.4000 | 0.1185 | 0.1858 | False | 15 |
| pooled vs always_up | held_out | 32 | mcnemar | 6.6176 | 0.0090 | 0.0240 | True | 34 |
| pooled vs always_up | held_out | 32 | mcnemar | 4.0238 | 0.0436 | 0.0820 | False | 42 |
| pooled vs always_up | held_out | 64 | mcnemar | 2.7692 | 0.0923 | 0.1606 | False | 13 |
| pooled vs always_up | held_out | 64 | mcnemar | 0.0625 | 0.8036 | 0.8944 | False | 16 |
| pooled vs always_up | held_out | 64 | mcnemar | 2.3256 | 0.1263 | 0.1922 | False | 43 |
| pooled vs always_up | held_out | 128 | mcnemar | 0.0000 | 1.0000 | 1.0000 | False | 5 |
| pooled vs always_up | held_out | 128 | mcnemar | 3.2000 | 0.0625 | 0.1145 | False | 5 |
| pooled vs always_up | held_out | 128 | mcnemar | 4.0500 | 0.0414 | 0.0801 | False | 20 |
| pooled vs zero_shot | held_out | 2 | diebold_mariano | 2.8785 | 0.0040 | 0.0123 | True | 312 |
| pooled vs zero_shot | held_out | 2 | diebold_mariano | 2.4599 | 0.0139 | 0.0353 | True | 315 |
| pooled vs zero_shot | held_out | 2 | diebold_mariano | 2.2084 | 0.0272 | 0.0575 | False | 321 |
| pooled vs zero_shot | held_out | 4 | diebold_mariano | -0.9609 | 0.3366 | 0.4328 | False | 312 |
| pooled vs zero_shot | held_out | 4 | diebold_mariano | 3.5499 | 0.0004 | 0.0015 | True | 315 |
| pooled vs zero_shot | held_out | 4 | diebold_mariano | -0.1410 | 0.8879 | 0.9573 | False | 321 |
| pooled vs zero_shot | held_out | 8 | diebold_mariano | -2.4707 | 0.0135 | 0.0353 | True | 312 |
| pooled vs zero_shot | held_out | 8 | diebold_mariano | -2.1303 | 0.0331 | 0.0666 | False | 315 |
| pooled vs zero_shot | held_out | 8 | diebold_mariano | -3.8939 | 0.0001 | 0.0006 | True | 321 |
| pooled vs zero_shot | held_out | 16 | diebold_mariano | -1.6711 | 0.0947 | 0.1606 | False | 312 |
| pooled vs zero_shot | held_out | 16 | diebold_mariano | -2.4144 | 0.0158 | 0.0384 | True | 315 |
| pooled vs zero_shot | held_out | 16 | diebold_mariano | -1.6672 | 0.0955 | 0.1606 | False | 321 |
| pooled vs zero_shot | held_out | 32 | diebold_mariano | -6.0277 | 0.0000 | 0.0000 | True | 312 |
| pooled vs zero_shot | held_out | 32 | diebold_mariano | -0.9753 | 0.3294 | 0.4261 | False | 315 |
| pooled vs zero_shot | held_out | 32 | diebold_mariano | -3.5028 | 0.0005 | 0.0018 | True | 321 |
| pooled vs zero_shot | held_out | 64 | diebold_mariano | -3.9178 | 0.0001 | 0.0005 | True | 312 |
| pooled vs zero_shot | held_out | 64 | diebold_mariano | 0.0613 | 0.9511 | 0.9994 | False | 315 |
| pooled vs zero_shot | held_out | 64 | diebold_mariano | -3.0440 | 0.0023 | 0.0074 | True | 321 |
| pooled vs zero_shot | held_out | 128 | diebold_mariano | -6.2894 | 0.0000 | 0.0000 | True | 312 |
| pooled vs zero_shot | held_out | 128 | diebold_mariano | -0.9406 | 0.3469 | 0.4433 | False | 315 |
| pooled vs zero_shot | held_out | 128 | diebold_mariano | -4.8347 | 0.0000 | 0.0000 | True | 321 |
| per_sector vs always_up | seen | 2 | mcnemar | 4.3682 | 0.0364 | 0.0717 | False | 220 |
| per_sector vs always_up | seen | 2 | mcnemar | 17.2565 | 0.0000 | 0.0002 | True | 230 |
| per_sector vs always_up | seen | 2 | mcnemar | 48.3357 | 0.0000 | 0.0000 | True | 429 |
| per_sector vs always_up | seen | 4 | mcnemar | 10.9637 | 0.0009 | 0.0033 | True | 193 |
| per_sector vs always_up | seen | 4 | mcnemar | 2.0124 | 0.1558 | 0.2271 | False | 161 |
| per_sector vs always_up | seen | 4 | mcnemar | 4.0157 | 0.0449 | 0.0837 | False | 255 |
| per_sector vs always_up | seen | 8 | mcnemar | 17.7515 | 0.0000 | 0.0002 | True | 334 |
| per_sector vs always_up | seen | 8 | mcnemar | 0.7626 | 0.3825 | 0.4799 | False | 257 |
| per_sector vs always_up | seen | 8 | mcnemar | 61.7013 | 0.0000 | 0.0000 | True | 452 |
| per_sector vs always_up | seen | 16 | mcnemar | 0.7829 | 0.3763 | 0.4750 | False | 327 |
| per_sector vs always_up | seen | 16 | mcnemar | 0.2591 | 0.6108 | 0.7309 | False | 247 |
| per_sector vs always_up | seen | 16 | mcnemar | 44.9019 | 0.0000 | 0.0000 | True | 418 |
| per_sector vs always_up | seen | 32 | mcnemar | 42.3322 | 0.0000 | 0.0000 | True | 307 |
| per_sector vs always_up | seen | 32 | mcnemar | 0.0176 | 0.8944 | 0.9593 | False | 227 |
| per_sector vs always_up | seen | 32 | mcnemar | 20.9518 | 0.0000 | 0.0000 | True | 353 |
| per_sector vs always_up | seen | 64 | mcnemar | 21.6701 | 0.0000 | 0.0000 | True | 288 |
| per_sector vs always_up | seen | 64 | mcnemar | 1.5148 | 0.2183 | 0.3012 | False | 169 |
| per_sector vs always_up | seen | 64 | mcnemar | 7.3146 | 0.0067 | 0.0199 | True | 302 |
| per_sector vs always_up | seen | 128 | mcnemar | 67.2042 | 0.0000 | 0.0000 | True | 240 |
| per_sector vs always_up | seen | 128 | mcnemar | 2.3650 | 0.1238 | 0.1898 | False | 137 |
| per_sector vs always_up | seen | 128 | mcnemar | 25.6709 | 0.0000 | 0.0000 | True | 237 |
| per_sector vs pooled | seen | 2 | diebold_mariano | -3.6906 | 0.0002 | 0.0011 | True | 1116 |
| per_sector vs pooled | seen | 2 | diebold_mariano | -1.0374 | 0.2996 | 0.4001 | False | 1143 |
| per_sector vs pooled | seen | 2 | diebold_mariano | -6.1584 | 0.0000 | 0.0000 | True | 1164 |
| per_sector vs pooled | seen | 4 | diebold_mariano | 3.5616 | 0.0004 | 0.0015 | True | 1116 |
| per_sector vs pooled | seen | 4 | diebold_mariano | -0.3787 | 0.7049 | 0.8061 | False | 1143 |
| per_sector vs pooled | seen | 4 | diebold_mariano | 0.1724 | 0.8631 | 0.9403 | False | 1164 |
| per_sector vs pooled | seen | 8 | diebold_mariano | 4.7987 | 0.0000 | 0.0000 | True | 1116 |
| per_sector vs pooled | seen | 8 | diebold_mariano | 2.9962 | 0.0027 | 0.0086 | True | 1143 |
| per_sector vs pooled | seen | 8 | diebold_mariano | 5.2186 | 0.0000 | 0.0000 | True | 1164 |
| per_sector vs pooled | seen | 16 | diebold_mariano | -0.2246 | 0.8223 | 0.9102 | False | 1116 |
| per_sector vs pooled | seen | 16 | diebold_mariano | 2.2702 | 0.0232 | 0.0505 | False | 1143 |
| per_sector vs pooled | seen | 16 | diebold_mariano | 2.3025 | 0.0213 | 0.0479 | True | 1164 |
| per_sector vs pooled | seen | 32 | diebold_mariano | 3.7888 | 0.0002 | 0.0008 | True | 1116 |
| per_sector vs pooled | seen | 32 | diebold_mariano | 2.4511 | 0.0142 | 0.0355 | True | 1143 |
| per_sector vs pooled | seen | 32 | diebold_mariano | 1.6724 | 0.0944 | 0.1606 | False | 1164 |
| per_sector vs pooled | seen | 64 | diebold_mariano | 1.5482 | 0.1216 | 0.1878 | False | 1116 |
| per_sector vs pooled | seen | 64 | diebold_mariano | 2.4577 | 0.0140 | 0.0353 | True | 1143 |
| per_sector vs pooled | seen | 64 | diebold_mariano | -0.0818 | 0.9348 | 0.9873 | False | 1164 |
| per_sector vs pooled | seen | 128 | diebold_mariano | 2.6864 | 0.0072 | 0.0209 | True | 1116 |
| per_sector vs pooled | seen | 128 | diebold_mariano | 2.1874 | 0.0287 | 0.0594 | False | 1143 |
| per_sector vs pooled | seen | 128 | diebold_mariano | 1.6333 | 0.1024 | 0.1656 | False | 1164 |
| per_sector vs zero_shot | seen | 2 | diebold_mariano | 1.6246 | 0.1042 | 0.1673 | False | 1116 |
| per_sector vs zero_shot | seen | 2 | diebold_mariano | 3.6060 | 0.0003 | 0.0013 | True | 1143 |
| per_sector vs zero_shot | seen | 2 | diebold_mariano | -2.6616 | 0.0078 | 0.0218 | True | 1164 |
| per_sector vs zero_shot | seen | 4 | diebold_mariano | 1.6043 | 0.1086 | 0.1727 | False | 1116 |
| per_sector vs zero_shot | seen | 4 | diebold_mariano | 3.2901 | 0.0010 | 0.0036 | True | 1143 |
| per_sector vs zero_shot | seen | 4 | diebold_mariano | -1.8418 | 0.0655 | 0.1169 | False | 1164 |
| per_sector vs zero_shot | seen | 8 | diebold_mariano | -1.6014 | 0.1093 | 0.1727 | False | 1116 |
| per_sector vs zero_shot | seen | 8 | diebold_mariano | -3.1677 | 0.0015 | 0.0053 | True | 1143 |
| per_sector vs zero_shot | seen | 8 | diebold_mariano | -1.5572 | 0.1194 | 0.1859 | False | 1164 |
| per_sector vs zero_shot | seen | 16 | diebold_mariano | -1.0329 | 0.3016 | 0.4003 | False | 1116 |
| per_sector vs zero_shot | seen | 16 | diebold_mariano | -2.4321 | 0.0150 | 0.0370 | True | 1143 |
| per_sector vs zero_shot | seen | 16 | diebold_mariano | -1.6598 | 0.0970 | 0.1606 | False | 1164 |
| per_sector vs zero_shot | seen | 32 | diebold_mariano | -3.7519 | 0.0002 | 0.0008 | True | 1116 |
| per_sector vs zero_shot | seen | 32 | diebold_mariano | -3.7822 | 0.0002 | 0.0008 | True | 1143 |
| per_sector vs zero_shot | seen | 32 | diebold_mariano | -3.3981 | 0.0007 | 0.0026 | True | 1164 |
| per_sector vs zero_shot | seen | 64 | diebold_mariano | -0.2150 | 0.8298 | 0.9136 | False | 1116 |
| per_sector vs zero_shot | seen | 64 | diebold_mariano | -0.3991 | 0.6898 | 0.7933 | False | 1143 |
| per_sector vs zero_shot | seen | 64 | diebold_mariano | -4.5301 | 0.0000 | 0.0001 | True | 1164 |
| per_sector vs zero_shot | seen | 128 | diebold_mariano | -2.7457 | 0.0060 | 0.0181 | True | 1116 |
| per_sector vs zero_shot | seen | 128 | diebold_mariano | 0.0906 | 0.9278 | 0.9849 | False | 1143 |
| per_sector vs zero_shot | seen | 128 | diebold_mariano | -4.0828 | 0.0000 | 0.0003 | True | 1164 |
| pooled vs always_up | seen | 2 | mcnemar | 7.0175 | 0.0075 | 0.0213 | True | 57 |
| pooled vs always_up | seen | 2 | mcnemar | 9.5629 | 0.0019 | 0.0063 | True | 151 |
| pooled vs always_up | seen | 2 | mcnemar | 10.4143 | 0.0011 | 0.0039 | True | 70 |
| pooled vs always_up | seen | 4 | mcnemar | 9.1321 | 0.0022 | 0.0072 | True | 53 |
| pooled vs always_up | seen | 4 | mcnemar | 0.0238 | 0.8776 | 0.9511 | False | 42 |
| pooled vs always_up | seen | 4 | mcnemar | 0.0000 | 1.0000 | 1.0000 | False | 75 |
| pooled vs always_up | seen | 8 | mcnemar | 2.0206 | 0.1548 | 0.2271 | False | 97 |
| pooled vs always_up | seen | 8 | mcnemar | 3.4057 | 0.0645 | 0.1160 | False | 106 |
| pooled vs always_up | seen | 8 | mcnemar | 13.4378 | 0.0002 | 0.0011 | True | 217 |
| pooled vs always_up | seen | 16 | mcnemar | 7.6220 | 0.0054 | 0.0165 | True | 82 |
| pooled vs always_up | seen | 16 | mcnemar | 6.9638 | 0.0081 | 0.0219 | True | 138 |
| pooled vs always_up | seen | 16 | mcnemar | 19.0476 | 0.0000 | 0.0001 | True | 189 |
| pooled vs always_up | seen | 32 | mcnemar | 2.1316 | 0.1433 | 0.2134 | False | 38 |
| pooled vs always_up | seen | 32 | mcnemar | 9.7524 | 0.0017 | 0.0056 | True | 105 |
| pooled vs always_up | seen | 32 | mcnemar | 17.0068 | 0.0000 | 0.0002 | True | 147 |
| pooled vs always_up | seen | 64 | mcnemar | 8.8276 | 0.0023 | 0.0074 | True | 29 |
| pooled vs always_up | seen | 64 | mcnemar | 0.0816 | 0.7754 | 0.8715 | False | 49 |
| pooled vs always_up | seen | 64 | mcnemar | 14.6402 | 0.0001 | 0.0006 | True | 164 |
| pooled vs always_up | seen | 128 | mcnemar | 1.7857 | 0.1796 | 0.2546 | False | 14 |
| pooled vs always_up | seen | 128 | mcnemar | 0.0000 | 1.0000 | 1.0000 | False | 17 |
| pooled vs always_up | seen | 128 | mcnemar | 18.2785 | 0.0000 | 0.0001 | True | 79 |
| pooled vs zero_shot | seen | 2 | diebold_mariano | 3.7783 | 0.0002 | 0.0008 | True | 1116 |
| pooled vs zero_shot | seen | 2 | diebold_mariano | 5.3478 | 0.0000 | 0.0000 | True | 1143 |
| pooled vs zero_shot | seen | 2 | diebold_mariano | 4.1581 | 0.0000 | 0.0002 | True | 1164 |
| pooled vs zero_shot | seen | 4 | diebold_mariano | -2.0193 | 0.0435 | 0.0820 | False | 1116 |
| pooled vs zero_shot | seen | 4 | diebold_mariano | 4.1646 | 0.0000 | 0.0002 | True | 1143 |
| pooled vs zero_shot | seen | 4 | diebold_mariano | -1.3861 | 0.1657 | 0.2399 | False | 1164 |
| pooled vs zero_shot | seen | 8 | diebold_mariano | -4.8840 | 0.0000 | 0.0000 | True | 1116 |
| pooled vs zero_shot | seen | 8 | diebold_mariano | -4.8724 | 0.0000 | 0.0000 | True | 1143 |
| pooled vs zero_shot | seen | 8 | diebold_mariano | -4.7660 | 0.0000 | 0.0000 | True | 1164 |
| pooled vs zero_shot | seen | 16 | diebold_mariano | -0.5214 | 0.6021 | 0.7246 | False | 1116 |
| pooled vs zero_shot | seen | 16 | diebold_mariano | -7.3494 | 0.0000 | 0.0000 | True | 1143 |
| pooled vs zero_shot | seen | 16 | diebold_mariano | -2.2944 | 0.0218 | 0.0483 | True | 1164 |
| pooled vs zero_shot | seen | 32 | diebold_mariano | -5.7130 | 0.0000 | 0.0000 | True | 1116 |
| pooled vs zero_shot | seen | 32 | diebold_mariano | -5.8778 | 0.0000 | 0.0000 | True | 1143 |
| pooled vs zero_shot | seen | 32 | diebold_mariano | -3.8594 | 0.0001 | 0.0006 | True | 1164 |
| pooled vs zero_shot | seen | 64 | diebold_mariano | -1.1421 | 0.2534 | 0.3429 | False | 1116 |
| pooled vs zero_shot | seen | 64 | diebold_mariano | -1.7054 | 0.0881 | 0.1559 | False | 1143 |
| pooled vs zero_shot | seen | 64 | diebold_mariano | -3.9661 | 0.0001 | 0.0005 | True | 1164 |
| pooled vs zero_shot | seen | 128 | diebold_mariano | -3.7668 | 0.0002 | 0.0008 | True | 1116 |
| pooled vs zero_shot | seen | 128 | diebold_mariano | -2.0270 | 0.0427 | 0.0818 | False | 1143 |
| pooled vs zero_shot | seen | 128 | diebold_mariano | -3.6138 | 0.0003 | 0.0013 | True | 1164 |
