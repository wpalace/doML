# Phase 22 Audit — Pre-flight Wheel Validation & Lockfile Bootstrap

**Generated:** 2026-04-30
**Resolved Python version:** 3.14
**Resolved scipy-notebook tag:** quay.io/jupyter/scipy-notebook:2026-04-27

This document captures the three raw audit artifacts produced by the pre-flight rig in plan 22-02. Per D-22-16, this is a single-file audit (no `audit/` subdirectory). Per D-22-17, the three sections are: mamba list, conflict diff, uv pip compile diff. The go/no-go decision and Python version rationale live in `22-SUMMARY.md`.

## Mamba List

Full `mamba list` output from the throwaway `quay.io/jupyter/scipy-notebook:<tag>` container. Surfaces the conda-managed package set that the v1.6 Dockerfile install layer (Phase 23) will overlay with `uv pip install --system`.

```text
Entered start.sh with args: mamba list
Running hooks in: /usr/local/bin/start-notebook.d as uid: 1000 gid: 100
Done running hooks in: /usr/local/bin/start-notebook.d
Running hooks in: /usr/local/bin/before-notebook.d as uid: 1000 gid: 100
Sourcing shell script: /usr/local/bin/before-notebook.d/10activate-conda-env.sh
Done running hooks in: /usr/local/bin/before-notebook.d
Executing the command: mamba list
List of packages in environment: "/opt/conda"

  Name                              Version       Build                    Channel    
────────────────────────────────────────────────────────────────────────────────────────
  _openmp_mutex                     4.5           20_gnu                   conda-forge
  _python_abi3_support              1.0           hd8ed1ab_2               conda-forge
  alembic                           1.18.4        pyhcf101f3_0             conda-forge
  altair                            6.1.0         pyhd8ed1ab_0             conda-forge
  annotated-types                   0.7.0         pyhd8ed1ab_1             conda-forge
  anyio                             4.13.0        pyhcf101f3_0             conda-forge
  aom                               3.9.1         hac33072_0               conda-forge
  archspec                          0.2.5         pyhd8ed1ab_0             conda-forge
  argon2-cffi                       25.1.0        pyhd8ed1ab_0             conda-forge
  argon2-cffi-bindings              25.1.0        py313h07c4f96_2          conda-forge
  arrow                             1.4.0         pyhcf101f3_0             conda-forge
  asttokens                         3.0.1         pyhd8ed1ab_0             conda-forge
  async-lru                         2.3.0         pyhcf101f3_0             conda-forge
  attrs                             26.1.0        pyhcf101f3_0             conda-forge
  aws-c-auth                        0.10.1        h2d2dd48_2               conda-forge
  aws-c-cal                         0.9.13        h2c9d079_1               conda-forge
  aws-c-common                      0.12.6        hb03c661_0               conda-forge
  aws-c-compression                 0.3.2         h8b1a151_0               conda-forge
  aws-c-event-stream                0.6.0         h9b893ba_1               conda-forge
  aws-c-http                        0.10.12       h4bacb7b_1               conda-forge
  aws-c-io                          0.26.3        hc87160b_0               conda-forge
  aws-c-mqtt                        0.15.2        he9ea9c5_1               conda-forge
  aws-c-s3                          0.11.5        h6d69fc9_5               conda-forge
  aws-c-sdkutils                    0.2.4         h8b1a151_4               conda-forge
  aws-checksums                     0.2.10        h8b1a151_0               conda-forge
  aws-crt-cpp                       0.37.4        h4c8aef7_3               conda-forge
  aws-sdk-cpp                       1.11.747      hc3785e1_3               conda-forge
  azure-core-cpp                    1.16.2        h206d751_0               conda-forge
  azure-identity-cpp                1.13.3        hed0cdb0_1               conda-forge
  azure-storage-blobs-cpp           12.16.0       hdd73cc9_1               conda-forge
  azure-storage-common-cpp          12.12.0       ha7a2c86_1               conda-forge
  azure-storage-files-datalake-cpp  12.14.0       h52c5a47_1               conda-forge
  babel                             2.18.0        pyhcf101f3_1             conda-forge
  backports.zstd                    1.3.0         py313h18e8e13_0          conda-forge
  beautifulsoup4                    4.14.3        pyha770c72_0             conda-forge
  blas                              2.306         openblas                 conda-forge
  blas-devel                        3.11.0        6_h1ea3ea9_openblas      conda-forge
  bleach                            6.3.0         pyhcf101f3_1             conda-forge
  bleach-with-css                   6.3.0         hbca2aae_1               conda-forge
  blinker                           1.9.0         pyhff2d567_0             conda-forge
  blosc                             1.21.6        he440d0b_1               conda-forge
  bokeh                             3.9.0         pyhd8ed1ab_0             conda-forge
  boltons                           25.0.0        pyhd8ed1ab_0             conda-forge
  bottleneck                        1.6.0         np2py313hc18bace_3       conda-forge
  brotli                            1.2.0         hed03a55_1               conda-forge
  brotli-bin                        1.2.0         hb03c661_1               conda-forge
  brotli-python                     1.2.0         py313hf159716_1          conda-forge
  brunsli                           0.1           hd1e3526_2               conda-forge
  bzip2                             1.0.8         hda65f42_9               conda-forge
  c-ares                            1.34.6        hb03c661_0               conda-forge
  c-blosc2                          2.23.1        hc31b594_0               conda-forge
  ca-certificates                   2026.4.22     hbd8a1cb_0               conda-forge
  cached-property                   1.5.2         hd8ed1ab_1               conda-forge
  cached_property                   1.5.2         pyha770c72_1             conda-forge
  certifi                           2026.4.22     pyhd8ed1ab_0             conda-forge
  certipy                           0.2.2         pyhd8ed1ab_0             conda-forge
  cffi                              2.0.0         py313hf46b229_1          conda-forge
  charls                            2.4.3         hecca717_0               conda-forge
  charset-normalizer                3.4.7         pyhd8ed1ab_0             conda-forge
  click                             8.3.3         pyhc90fa1f_0             conda-forge
  cloudpickle                       3.1.2         pyhcf101f3_1             conda-forge
  colorama                          0.4.6         pyhd8ed1ab_1             conda-forge
  comm                              0.2.3         pyhe01879c_0             conda-forge
  conda                             26.3.2        py313h78bf25f_0          conda-forge
  conda-libmamba-solver             26.4.0        pyhd8ed1ab_0             conda-forge
  conda-package-handling            2.4.0         pyh7900ff3_2             conda-forge
  conda-package-streaming           0.12.0        pyhd8ed1ab_0             conda-forge
  contourpy                         1.3.3         py313hc8edb43_4          conda-forge
  cpp-expected                      1.3.1         h171cf75_0               conda-forge
  cpython                           3.13.13       py313hd8ed1ab_100        conda-forge
  cryptography                      47.0.0        py313heb322e3_0          conda-forge
  cycler                            0.12.1        pyhcf101f3_2             conda-forge
  cython                            3.2.4         py313hc80a56d_0          conda-forge
  cytoolz                           1.1.0         py313h07c4f96_2          conda-forge
  dask                              2026.3.0      pyhc364b38_0             conda-forge
  dask-core                         2026.3.0      pyhc364b38_0             conda-forge
  dav1d                             1.2.1         hd590300_0               conda-forge
  debugpy                           1.8.20        py313h5d5ffb9_0          conda-forge
  decorator                         5.2.1         pyhd8ed1ab_0             conda-forge
  defusedxml                        0.7.1         pyhd8ed1ab_0             conda-forge
  dill                              0.4.1         pyhcf101f3_0             conda-forge
  distributed                       2026.3.0      pyhc364b38_0             conda-forge
  distro                            1.9.0         pyhd8ed1ab_1             conda-forge
  et_xmlfile                        2.0.0         pyhd8ed1ab_1             conda-forge
  exceptiongroup                    1.3.1         pyhd8ed1ab_0             conda-forge
  executing                         2.2.1         pyhd8ed1ab_0             conda-forge
  fmt                               12.1.0        hff5e90c_0               conda-forge
  fonttools                         4.62.1        py313h3dea7bd_0          conda-forge
  fqdn                              1.5.1         pyhd8ed1ab_1             conda-forge
  freetype                          2.14.3        ha770c72_0               conda-forge
  frozendict                        2.4.7         py313h07c4f96_0          conda-forge
  fsspec                            2026.3.0      pyhd8ed1ab_0             conda-forge
  gflags                            2.2.2         h5888daf_1005            conda-forge
  giflib                            5.2.2         hd590300_0               conda-forge
  gitdb                             4.0.12        pyhd8ed1ab_0             conda-forge
  gitpython                         3.1.47        pyhd8ed1ab_0             conda-forge
  glog                              0.7.1         hbabe93e_0               conda-forge
  gmp                               6.3.0         hac33072_2               conda-forge
  gmpy2                             2.3.0         py313h86d8783_1          conda-forge
  greenlet                          3.4.0         py313h5d5ffb9_0          conda-forge
  h11                               0.16.0        pyhcf101f3_1             conda-forge
  h2                                4.3.0         pyhcf101f3_0             conda-forge
  h5py                              3.16.0        nompi_py313h22c32d4_102  conda-forge
  hdf5                              2.1.0         nompi_hd4fcb43_104       conda-forge
  hpack                             4.1.0         pyhd8ed1ab_0             conda-forge
  httpcore                          1.0.9         pyh29332c3_0             conda-forge
  httpx                             0.28.1        pyhd8ed1ab_0             conda-forge
  hyperframe                        6.1.0         pyhd8ed1ab_0             conda-forge
  icu                               78.3          h33c6efd_0               conda-forge
  idna                              3.13          pyhcf101f3_0             conda-forge
  imagecodecs                       2026.3.6      py313h0924926_2          conda-forge
  imageio                           2.37.0        pyhfb79c49_0             conda-forge
  importlib-metadata                8.8.0         pyhcf101f3_0             conda-forge
  importlib_resources               7.1.0         pyhd8ed1ab_0             conda-forge
  ipykernel                         7.2.0         pyha191276_1             conda-forge
  ipympl                            0.10.0        pyhcf101f3_0             conda-forge
  ipython                           9.13.0        pyh53cf698_0             conda-forge
  ipython_genutils                  0.2.0         pyhd8ed1ab_2             conda-forge
  ipython_pygments_lexers           1.1.1         pyhd8ed1ab_0             conda-forge
  ipywidgets                        8.1.8         pyhd8ed1ab_0             conda-forge
  isoduration                       20.11.0       pyhd8ed1ab_1             conda-forge
  jedi                              0.19.2        pyhd8ed1ab_1             conda-forge
  jinja2                            3.1.6         pyhcf101f3_1             conda-forge
  joblib                            1.5.3         pyhd8ed1ab_0             conda-forge
  json5                             0.14.0        pyhd8ed1ab_0             conda-forge
  jsonpatch                         1.33          pyhd8ed1ab_1             conda-forge
  jsonpointer                       3.1.1         pyhcf101f3_0             conda-forge
  jsonschema                        4.26.0        pyhcf101f3_0             conda-forge
  jsonschema-specifications         2025.9.1      pyhcf101f3_0             conda-forge
  jsonschema-with-format-nongpl     4.26.0        hcf101f3_0               conda-forge
  jupyter-lsp                       2.3.1         pyhcf101f3_0             conda-forge
  jupyter_client                    8.8.0         pyhcf101f3_0             conda-forge
  jupyter_core                      5.9.1         pyhc90fa1f_0             conda-forge
  jupyter_events                    0.12.1        pyhcf101f3_0             conda-forge
  jupyter_server                    2.17.0        pyhcf101f3_0             conda-forge
  jupyter_server_terminals          0.5.4         pyhcf101f3_0             conda-forge
  jupyterhub-base                   5.4.4         pyhc90fa1f_0             conda-forge
  jupyterhub-singleuser             5.4.4         h942873f_0               conda-forge
  jupyterlab                        4.5.6         pyhd8ed1ab_0             conda-forge
  jupyterlab-git                    0.52.0        pyhd8ed1ab_0             conda-forge
  jupyterlab_pygments               0.3.0         pyhd8ed1ab_2             conda-forge
  jupyterlab_server                 2.28.0        pyhcf101f3_0             conda-forge
  jupyterlab_widgets                3.0.16        pyhcf101f3_1             conda-forge
  jxrlib                            1.1           hd590300_3               conda-forge
  keyutils                          1.6.3         hb9d3cd8_0               conda-forge
  kiwisolver                        1.5.0         py313hc8edb43_0          conda-forge
  krb5                              1.22.2        ha1258a1_0               conda-forge
  lark                              1.3.1         pyhd8ed1ab_0             conda-forge
  lazy-loader                       0.5           pyhd8ed1ab_0             conda-forge
  lcms2                             2.19          h0c24ade_0               conda-forge
  ld_impl_linux-64                  2.45.1        default_hbd61a6d_102     conda-forge
  lerc                              4.1.0         hdb68285_0               conda-forge
  libabseil                         20260107.1    cxx17_h7b12aa8_0         conda-forge
  libaec                            1.1.5         h088129d_0               conda-forge
  libarchive                        3.8.7         gpl_hc2c16d8_100         conda-forge
  libarrow                          24.0.0        ha7f89c6_0_cpu           conda-forge
  libarrow-acero                    24.0.0        h635bf11_0_cpu           conda-forge
  libarrow-compute                  24.0.0        h53684a4_0_cpu           conda-forge
  libarrow-dataset                  24.0.0        h635bf11_0_cpu           conda-forge
  libarrow-substrait                24.0.0        hb4dd7c2_0_cpu           conda-forge
  libavif16                         1.4.1         hcfa2d63_0               conda-forge
  libblas                           3.11.0        6_h4a7cf45_openblas      conda-forge
  libbrotlicommon                   1.2.0         hb03c661_1               conda-forge
  libbrotlidec                      1.2.0         hb03c661_1               conda-forge
  libbrotlienc                      1.2.0         hb03c661_1               conda-forge
  libcblas                          3.11.0        6_h0358290_openblas      conda-forge
  libcrc32c                         1.1.2         h9c3ff4c_0               conda-forge
  libcurl                           8.19.0        hcf29cc6_0               conda-forge
  libdeflate                        1.25          h17f619e_0               conda-forge
  libedit                           3.1.20250104  pl5321h7949ede_0         conda-forge
  libev                             4.33          hd590300_2               conda-forge
  libevent                          2.1.12        hf998b51_1               conda-forge
  libexpat                          2.7.5         hecca717_0               conda-forge
  libffi                            3.5.2         h3435931_0               conda-forge
  libfreetype                       2.14.3        ha770c72_0               conda-forge
  libfreetype6                      2.14.3        h73754d4_0               conda-forge
  libgcc                            15.2.0        he0feb66_18              conda-forge
  libgcc-ng                         15.2.0        h69a702a_18              conda-forge
  libgfortran                       15.2.0        h69a702a_18              conda-forge
  libgfortran5                      15.2.0        h68bc16d_18              conda-forge
  libgomp                           15.2.0        he0feb66_18              conda-forge
  libgoogle-cloud                   3.3.0         h25dbb67_1               conda-forge
  libgoogle-cloud-storage           3.3.0         hdbdcf42_1               conda-forge
  libgrpc                           1.78.1        h1d1128b_0               conda-forge
  libhwy                            1.4.0         h10be129_0               conda-forge
  libiconv                          1.18          h3b78370_2               conda-forge
  libjpeg-turbo                     3.1.4.1       hb03c661_0               conda-forge
  libjxl                            0.11.2        h174a0a3_1               conda-forge
  liblapack                         3.11.0        6_h47877c9_openblas      conda-forge
  liblapacke                        3.11.0        6_h6ae95b6_openblas      conda-forge
  liblzma                           5.8.3         hb03c661_0               conda-forge
  libmamba                          2.5.0         hd28c85e_0               conda-forge
  libmamba-spdlog                   2.5.0         h12fcf84_0               conda-forge
  libmambapy                        2.5.0         py313h4616538_0          conda-forge
  libmpdec                          4.0.0         hb03c661_1               conda-forge
  libnghttp2                        1.68.1        h877daf1_0               conda-forge
  libopenblas                       0.3.32        pthreads_h94d23a6_0      conda-forge
  libopentelemetry-cpp              1.26.0        h9692893_0               conda-forge
  libopentelemetry-cpp-headers      1.26.0        ha770c72_0               conda-forge
  libparquet                        24.0.0        h7376487_0_cpu           conda-forge
  libpng                            1.6.58        h421ea60_0               conda-forge
  libprotobuf                       6.33.5        h2b00c02_0               conda-forge
  libre2-11                         2025.11.05    h0dc7533_1               conda-forge
  libsodium                         1.0.21        h280c20c_3               conda-forge
  libsolv                           0.7.37        h9463b59_0               conda-forge
  libsqlite                         3.53.0        hf4e2dac_0               conda-forge
  libssh2                           1.11.1        hcf80075_0               conda-forge
  libstdcxx                         15.2.0        h934c35e_18              conda-forge
  libstdcxx-ng                      15.2.0        hdf11a46_18              conda-forge
  libthrift                         0.22.0        h7d032f7_2               conda-forge
  libtiff                           4.7.1         h9d88235_1               conda-forge
  libutf8proc                       2.11.3        hfe17d71_0               conda-forge
  libuuid                           2.42          h5347b49_0               conda-forge
  libwebp-base                      1.6.0         hd42ef1d_0               conda-forge
  libxcb                            1.17.0        h8a09558_0               conda-forge
  libxml2                           2.15.3        h49c6c72_0               conda-forge
  libxml2-16                        2.15.3        hca6bf5a_0               conda-forge
  libzlib                           1.3.2         h25fd6f3_2               conda-forge
  libzopfli                         1.0.3         h9c3ff4c_0               conda-forge
  llvmlite                          0.47.0        py313hdd307be_1          conda-forge
  locket                            1.0.0         pyhd8ed1ab_0             conda-forge
  lz4                               4.4.5         py313h28739b2_1          conda-forge
  lz4-c                             1.10.0        h5888daf_1               conda-forge
  lzo                               2.10          h280c20c_1002            conda-forge
  mako                              1.3.11        pyhcf101f3_0             conda-forge
  mamba                             2.5.0         h9835478_0               conda-forge
  markupsafe                        3.0.3         py313h3dea7bd_1          conda-forge
  matplotlib-base                   3.10.9        py313h683a580_0          conda-forge
  matplotlib-inline                 0.2.1         pyhd8ed1ab_0             conda-forge
  menuinst                          2.4.2         py313h78bf25f_0          conda-forge
  mistune                           3.2.0         pyhcf101f3_0             conda-forge
  mpc                               1.4.0         he0a73b1_0               conda-forge
  mpfr                              4.2.2         he0a73b1_0               conda-forge
  mpmath                            1.4.1         pyhd8ed1ab_0             conda-forge
  msgpack-python                    1.1.2         py313h7037e92_1          conda-forge
  munkres                           1.1.4         pyhd8ed1ab_1             conda-forge
  narwhals                          2.20.0        pyhcf101f3_0             conda-forge
  nbclassic                         1.3.3         pyhcf101f3_0             conda-forge
  nbclient                          0.10.4        pyhd8ed1ab_0             conda-forge
  nbconvert-core                    7.17.1        pyhcf101f3_0             conda-forge
  nbdime                            4.0.4         pyhcf101f3_0             conda-forge
  nbformat                          5.10.4        pyhd8ed1ab_1             conda-forge
  ncurses                           6.5           h2d0b736_3               conda-forge
  nest-asyncio                      1.6.0         pyhd8ed1ab_1             conda-forge
  networkx                          3.6.1         pyhcf101f3_0             conda-forge
  nlohmann_json                     3.12.0        h54a6638_1               conda-forge
  nlohmann_json-abi                 3.12.0        h0f90c79_1               conda-forge
  nomkl                             1.0           h5ca1d4c_0               conda-forge
  notebook                          7.5.5         pyhcf101f3_0             conda-forge
  notebook-shim                     0.2.4         pyhd8ed1ab_1             conda-forge
  numba                             0.65.1        py313h5dce7c4_0          conda-forge
  numexpr                           2.14.1        py313h24ae7f9_101        conda-forge
  numpy                             2.4.3         py313hf6604e3_0          conda-forge
  oauthlib                          3.3.1         pyhd8ed1ab_0             conda-forge
  openblas                          0.3.32        pthreads_h6ec200e_0      conda-forge
  openjpeg                          2.5.4         h55fea9a_0               conda-forge
  openjph                           0.27.0        h8d634f6_0               conda-forge
  openpyxl                          3.1.5         py313ha4be090_3          conda-forge
  openssl                           3.6.2         h35e630c_0               conda-forge
  orc                               2.3.0         h21090e2_0               conda-forge
  overrides                         7.7.0         pyhd8ed1ab_1             conda-forge
  packaging                         26.2          pyhc364b38_0             conda-forge
  pamela                            1.2.0         pyhd8ed1ab_1             conda-forge
  pandas                            3.0.2         py313hbfd7664_0          conda-forge
  pandocfilters                     1.5.0         pyhd8ed1ab_0             conda-forge
  parso                             0.8.6         pyhcf101f3_0             conda-forge
  partd                             1.4.2         pyhd8ed1ab_0             conda-forge
  patsy                             1.0.2         pyhcf101f3_0             conda-forge
  pexpect                           4.9.0         pyhd8ed1ab_1             conda-forge
  pillow                            12.2.0        py313h80991f8_0          conda-forge
  pip                               26.0.1        pyh145f28c_0             conda-forge
  platformdirs                      4.9.6         pyhcf101f3_0             conda-forge
  pluggy                            1.6.0         pyhf9edf01_1             conda-forge
  prometheus-cpp                    1.3.0         ha5d0236_0               conda-forge
  prometheus_client                 0.25.0        pyhd8ed1ab_0             conda-forge
  prompt-toolkit                    3.0.52        pyha770c72_0             conda-forge
  protobuf                          6.33.5        py313hf481762_2          conda-forge
  psutil                            7.2.2         py313h54dd161_0          conda-forge
  pthread-stubs                     0.4           hb9d3cd8_1002            conda-forge
  ptyprocess                        0.7.0         pyhd8ed1ab_1             conda-forge
  pure_eval                         0.2.3         pyhd8ed1ab_1             conda-forge
  py-cpuinfo                        9.0.0         pyhd8ed1ab_1             conda-forge
  pyarrow                           24.0.0        py313h78bf25f_0          conda-forge
  pyarrow-core                      24.0.0        py313h98bfbea_0_cpu      conda-forge
  pybind11-abi                      11            hc364b38_1               conda-forge
  pycosat                           0.6.6         py313h07c4f96_3          conda-forge
  pycparser                         2.22          pyh29332c3_1             conda-forge
  pydantic                          2.13.3        pyhcf101f3_0             conda-forge
  pydantic-core                     2.46.3        py313h843e2db_0          conda-forge
  pygments                          2.20.0        pyhd8ed1ab_0             conda-forge
  pyjwt                             2.12.1        pyhcf101f3_0             conda-forge
  pyparsing                         3.3.2         pyhcf101f3_0             conda-forge
  pysocks                           1.7.1         pyha55dd90_7             conda-forge
  pytables                          3.11.1        py313h2669098_1          conda-forge
  python                            3.13.13       h6add32d_100_cp313       conda-forge
  python-dateutil                   2.9.0.post0   pyhe01879c_2             conda-forge
  python-fastjsonschema             2.21.2        pyhe01879c_0             conda-forge
  python-gil                        3.13.13       h4df99d1_100             conda-forge
  python-json-logger                2.0.7         pyhd8ed1ab_0             conda-forge
  python-tzdata                     2026.2        pyhd8ed1ab_0             conda-forge
  python_abi                        3.13          8_cp313                  conda-forge
  pyyaml                            6.0.3         py313h3dea7bd_1          conda-forge
  pyzmq                             27.1.0        py312hda471dd_2          conda-forge
  qhull                             2020.2        h434a139_5               conda-forge
  rav1e                             0.8.1         h1fbca29_0               conda-forge
  re2                               2025.11.05    h5301d42_1               conda-forge
  readline                          8.3           h853b02a_0               conda-forge
  referencing                       0.37.0        pyhcf101f3_0             conda-forge
  reproc                            14.2.7.post0  hb03c661_0               conda-forge
  reproc-cpp                        14.2.7.post0  hecca717_0               conda-forge
  requests                          2.33.1        pyhcf101f3_1             conda-forge
  rfc3339-validator                 0.1.4         pyhd8ed1ab_1             conda-forge
  rfc3986-validator                 0.1.1         pyh9f0ad1d_0             conda-forge
  rfc3987-syntax                    1.1.0         pyhe01879c_1             conda-forge
  rpds-py                           0.30.0        py313h843e2db_0          conda-forge
  ruamel.yaml                       0.18.17       py313h54dd161_2          conda-forge
  ruamel.yaml.clib                  0.2.15        py313h54dd161_1          conda-forge
  s2n                               1.7.1         h1cbb8d7_1               conda-forge
  scikit-image                      0.26.0        np2py313hb172dc5_0       conda-forge
  scikit-learn                      1.8.0         np2py313h16d504d_1       conda-forge
  scipy                             1.17.1        py313h4b8bb8b_0          conda-forge
  seaborn                           0.13.2        hd8ed1ab_3               conda-forge
  seaborn-base                      0.13.2        pyhd8ed1ab_3             conda-forge
  send2trash                        2.1.0         pyha191276_1             conda-forge
  setuptools                        82.0.1        pyh332efcf_0             conda-forge
  simdjson                          4.2.4         hb700be7_0               conda-forge
  six                               1.17.0        pyhe01879c_1             conda-forge
  smmap                             5.0.3         pyhd8ed1ab_0             conda-forge
  snappy                            1.2.2         h03e3b7b_1               conda-forge
  sniffio                           1.3.1         pyhd8ed1ab_2             conda-forge
  sortedcontainers                  2.4.0         pyhd8ed1ab_1             conda-forge
  soupsieve                         2.8.3         pyhd8ed1ab_0             conda-forge
  spdlog                            1.17.0        hab81395_1               conda-forge
  sqlalchemy                        2.0.49        py313h54dd161_0          conda-forge
  stack_data                        0.6.3         pyhd8ed1ab_1             conda-forge
  statsmodels                       0.14.6        py313h29aa505_0          conda-forge
  svt-av1                           4.0.1         hecca717_0               conda-forge
  sympy                             1.14.0        pyh2585a3b_106           conda-forge
  tblib                             3.2.2         pyhcf101f3_0             conda-forge
  terminado                         0.18.1        pyhc90fa1f_1             conda-forge
  threadpoolctl                     3.6.0         pyhecae5ae_0             conda-forge
  tifffile                          2026.4.11     pyhd8ed1ab_0             conda-forge
  tinycss2                          1.4.0         pyhd8ed1ab_0             conda-forge
  tk                                8.6.13        noxft_h366c992_103       conda-forge
  tomli                             2.4.1         pyhcf101f3_0             conda-forge
  toolz                             1.1.0         pyhd8ed1ab_1             conda-forge
  tornado                           6.5.5         py313h07c4f96_0          conda-forge
  tqdm                              4.67.3        pyh8f84b5b_0             conda-forge
  traitlets                         5.14.3        pyhd8ed1ab_1             conda-forge
  truststore                        0.10.4        pyhcf101f3_0             conda-forge
  typing-extensions                 4.15.0        h396c80c_0               conda-forge
  typing-inspection                 0.4.2         pyhcf101f3_2             conda-forge
  typing_extensions                 4.15.0        pyhcf101f3_0             conda-forge
  typing_utils                      0.1.0         pyhd8ed1ab_1             conda-forge
  tzdata                            2025c         hc9c84f9_1               conda-forge
  uri-template                      1.3.0         pyhd8ed1ab_1             conda-forge
  urllib3                           2.6.3         pyhd8ed1ab_0             conda-forge
  wcwidth                           0.6.0         pyhd8ed1ab_0             conda-forge
  webcolors                         25.10.0       pyhd8ed1ab_0             conda-forge
  webencodings                      0.5.1         pyhd8ed1ab_3             conda-forge
  websocket-client                  1.9.0         pyhd8ed1ab_0             conda-forge
  widgetsnbextension                4.0.15        pyhd8ed1ab_0             conda-forge
  xlrd                              2.0.2         pyhd8ed1ab_0             conda-forge
  xorg-libxau                       1.0.12        hb03c661_1               conda-forge
  xorg-libxdmcp                     1.1.5         hb03c661_1               conda-forge
  xyzservices                       2026.3.0      pyhd8ed1ab_0             conda-forge
  yaml                              0.2.5         h280c20c_3               conda-forge
  yaml-cpp                          0.8.0         h3f2d84a_0               conda-forge
  zeromq                            4.3.5         h41580af_10              conda-forge
  zfp                               1.0.1         h909a3a2_5               conda-forge
  zict                              3.0.0         pyhd8ed1ab_1             conda-forge
  zipp                              3.23.1        pyhcf101f3_0             conda-forge
  zlib                              1.3.2         h25fd6f3_2               conda-forge
  zlib-ng                           2.3.3         hceb46e0_1               conda-forge
  zstandard                         0.25.0        py313h54dd161_1          conda-forge
  zstd                              1.5.7         hb78ec9c_6               conda-forge
```

## Conflict Diff

Intersection of conda packages (from `mamba list` above) and the package names in `requirements.in` (root). Each entry below appears in BOTH the conda base and DoML's explicit pip-managed deps — these are potential shadowing surfaces. Per D-22-03 we use `uv pip install --system` (additive) so conda versions are not pruned, but the listed packages may be upgraded by uv if requirements.in resolves to a newer version.

```text
jinja2
mistune
numpy
statsmodels
```

## uv pip compile Diff

Diff between the v1.5 `requirements.txt` (pip-compile format) and the v1.6 `requirements.txt` (uv format with `--generate-hashes`). Per PITFALLS.md §6 this diff is intentionally noisy — header format, ordering, comment style all change in addition to any semantic delta. The single-isolated commit (D-22-18 commit 2) absorbs the noise.

```diff
diff --git a/requirements.txt b/requirements.txt
index f8c246e..2173e2f 100644
--- a/requirements.txt
+++ b/requirements.txt
@@ -1,133 +1,1959 @@
-#
-# This file is autogenerated by pip-compile with Python 3.12
-# by the following command:
-#
-#    pip-compile --no-annotate --output-file=requirements.txt requirements.in
-#
-aiohappyeyeballs==2.6.1
-aiohttp==3.13.5
-aiosignal==1.4.0
-alembic==1.18.4
-annotated-types==0.7.0
-ansicolors==1.1.8
-attrs==26.1.0
-beautifulsoup4==4.14.3
-bleach==6.3.0
-build==1.4.2
-certifi==2026.2.25
-cfgv==3.5.0
-charset-normalizer==3.4.7
-click==8.3.2
-cloudpickle==3.1.2
-cmdstanpy==1.3.0
-colorlog==6.10.1
-contourpy==1.3.3
-cycler==0.12.1
-dacite==1.9.2
-defusedxml==0.7.1
-distlib==0.4.0
-duckdb==1.5.1
-entrypoints==0.4
-fastjsonschema==2.21.2
-filelock==3.25.2
-filetype==1.2.0
-fonttools==4.62.1
-frozenlist==1.8.0
-greenlet==3.3.2
-holidays==0.93
-identify==2.6.18
-idna==3.11
-imagehash==4.3.2
-importlib-resources==6.5.2
-iniconfig==2.3.0
-jinja2==3.1.6
-joblib==1.5.3
-jsonschema==4.26.0
-jsonschema-specifications==2025.9.1
-jupyter-client==8.8.0
-jupyter-core==5.9.1
-jupyterlab-pygments==0.3.0
-kiwisolver==1.5.0
-lightgbm==4.5.0
-llvmlite==0.45.1
-mako==1.3.10
-markupsafe==3.0.3
-matplotlib==3.10.0
-minify-html==0.18.1
-mistune==2.0.5
-multidict==6.7.1
-multimethod==1.12
-nbclient==0.10.4
-nbconvert==7.16.4
-nbformat==5.10.4
-nbstripout==0.9.1
-networkx==3.6.1
-nodeenv==1.10.0
-numba==0.62.1
-numpy==2.3.5
-nvidia-nccl-cu12==2.29.7
-optuna==3.6.1
-packaging==26.0
-pandas==2.3.3
-pandocfilters==1.5.1
-papermill==2.6.0
-patsy==1.0.2
-phik==0.12.5
-pillow==12.2.0
-pip-tools==7.4.1
-platformdirs==4.9.4
-plotly==5.24.1
-pluggy==1.6.0
-pre-commit==4.5.1
-propcache==0.4.1
-prophet==1.3.0
-puremagic==2.1.1
-pydantic==2.12.5
-pydantic-core==2.41.5
-pygments==2.20.0
-pynndescent==0.6.0
-pyparsing==3.3.2
-pyproject-hooks==1.2.0
-pytest==9.0.2
-python-dateutil==2.9.0.post0
-python-discovery==1.2.1
-pytz==2026.1.post1
-pywavelets==1.9.0
-pyyaml==6.0.3
-pyzmq==27.1.0
-referencing==0.37.0
-requests==2.33.1
-rpds-py==0.30.0
-scikit-learn==1.8.0
-scipy==1.16.3
-seaborn==0.13.2
-shap==0.47.2
-six==1.17.0
-slicer==0.0.8
-soupsieve==2.8.3
-sqlalchemy==2.0.49
-stanio==0.5.1
-statsmodels==0.14.4
-tenacity==9.1.4
-threadpoolctl==3.6.0
-tinycss2==1.5.1
-tornado==6.5.5
-tqdm==4.67.3
-traitlets==5.14.3
-typeguard==4.5.1
-typing-extensions==4.15.0
-typing-inspection==0.4.2
-tzdata==2026.1
-umap-learn==0.5.11
-urllib3==2.6.3
-virtualenv==21.2.0
-visions[type-image-path]==0.8.1
-webencodings==0.5.1
-wheel==0.46.3
-wordcloud==1.9.6
-xgboost==2.1.3
-yarl==1.23.0
-
-# The following packages are considered to be unsafe in a requirements file:
-# pip
-# setuptools
+# This file was autogenerated by uv via the following command:
+#    uv pip compile requirements.in --python-version 3.14 --generate-hashes -o /out/requirements-3.14.txt
+alembic==1.18.4 \
+    --hash=sha256:a5ed4adcf6d8a4cb575f3d759f071b03cd6e5c7618eb796cb52497be25bfe19a \
+    --hash=sha256:cb6e1fd84b6174ab8dbb2329f86d631ba9559dd78df550b57804d607672cedbc
+    # via optuna
+attrs==26.1.0 \
+    --hash=sha256:c647aa4a12dfbad9333ca4e71fe62ddc36f4e63b2d260a37a8b83d2f043ac309 \
+    --hash=sha256:d03ceb89cb322a8fd706d4fb91940737b6642aa36998fe130a9bc96c985eff32
+    # via
+    #   jsonschema
+    #   referencing
+bleach==6.3.0 \
+    --hash=sha256:6f3b91b1c0a02bb9a78b5a454c92506aa0fdf197e1d5e114d2e00c6f64306d22 \
+    --hash=sha256:fe10ec77c93ddf3d13a73b035abaac7a9f5e436513864ccdad516693213c65d6
+    # via kaggle
+certifi==2026.4.22 \
+    --hash=sha256:3cb2210c8f88ba2318d29b0388d1023c8492ff72ecdde4ebdaddbb13a31b1c4a \
+    --hash=sha256:8d455352a37b71bf76a79caa83a3d6c25afee4a385d632127b6afb3963f1c580
+    # via requests
+cfgv==3.5.0 \
+    --hash=sha256:a8dc6b26ad22ff227d2634a65cb388215ce6cc96bbcc5cfde7641ae87e8dacc0 \
+    --hash=sha256:d5b1034354820651caa73ede66a6294d6e95c1b00acc5e9b098e917404669132
+    # via pre-commit
+charset-normalizer==3.4.7 \
+    --hash=sha256:007d05ec7321d12a40227aae9e2bc6dca73f3cb21058999a1df9e193555a9dcc \
+    --hash=sha256:03853ed82eeebbce3c2abfdbc98c96dc205f32a79627688ac9a27370ea61a49c \
+    --hash=sha256:07d9e39b01743c3717745f4c530a6349eadbfa043c7577eef86c502c15df2c67 \
+    --hash=sha256:08e721811161356f97b4059a9ba7bafb23ea5ee2255402c42881c214e173c6b4 \
+    --hash=sha256:0c96c3b819b5c3e9e165495db84d41914d6894d55181d2d108cc1a69bfc9cce0 \
+    --hash=sha256:0ea948db76d31190bf08bd371623927ee1339d5f2a0b4b1b4a4439a65298703c \
+    --hash=sha256:0f7eb884681e3938906ed0434f20c63046eacd0111c4ba96f27b76084cd679f5 \
+    --hash=sha256:12a6fff75f6bc66711b73a2f0addfc4c8c15a20e805146a02d147a318962c444 \
+    --hash=sha256:12d8baf840cc7889b37c7c770f478adea7adce3dcb3944d02ec87508e2dcf153 \
+    --hash=sha256:14265bfe1f09498b9d8ec91e9ec9fa52775edf90fcbde092b25f4a33d444fea9 \
+    --hash=sha256:16d971e29578a5e97d7117866d15889a4a07befe0e87e703ed63cd90cb348c01 \
+    --hash=sha256:177a0ba5f0211d488e295aaf82707237e331c24788d8d76c96c5a41594723217 \
+    --hash=sha256:1a87ca9d5df6fe460483d9a5bbf2b18f620cbed41b432e2bddb686228282d10b \
+    --hash=sha256:1c2a768fdd44ee4a9339a9b0b130049139b8ce3c01d2ce09f67f5a68048d477c \
+    --hash=sha256:1c2aed2e5e41f24ea8ef1590b8e848a79b56f3a5564a65ceec43c9d692dc7d8a \
+    --hash=sha256:1dc8b0ea451d6e69735094606991f32867807881400f808a106ee1d963c46a83 \
+    --hash=sha256:1efde3cae86c8c273f1eb3b287be7d8499420cf2fe7585c41d370d3e790054a5 \
+    --hash=sha256:202389074300232baeb53ae2569a60901f7efadd4245cf3a3bf0617d60b439d7 \
+    --hash=sha256:203104ed3e428044fd943bc4bf45fa73c0730391f9621e37fe39ecf477b128cb \
+    --hash=sha256:2257141f39fe65a3fdf38aeccae4b953e5f3b3324f4ff0daf9f15b8518666a2c \
+    --hash=sha256:298930cec56029e05497a76988377cbd7457ba864beeea92ad7e844fe74cd1f1 \
+    --hash=sha256:2cd4a60d0e2fb04537162c62bbbb4182f53541fe0ede35cdf270a1c1e723cc42 \
+    --hash=sha256:2d6eb928e13016cea4f1f21d1e10c1cebd5a421bc57ddf5b1142ae3f86824fab \
+    --hash=sha256:2fe249cb4651fd12605b7288b24751d8bfd46d35f12a20b1ba33dea122e690df \
+    --hash=sha256:30b8d1d8c52a48c2c5690e152c169b673487a2a58de1ec7393196753063fcd5e \
+    --hash=sha256:320ade88cfb846b8cd6b4ddf5ee9e80ee0c1f52401f2456b84ae1ae6a1a5f207 \
+    --hash=sha256:3534e7dcbdcf757da6b85a0bbf5b6868786d5982dd959b065e65481644817a18 \
+    --hash=sha256:36836d6ff945a00b88ba1e4572d721e60b5b8c98c155d465f56ad19d68f23734 \
+    --hash=sha256:38c0109396c4cfc574d502df99742a45c72c08eff0a36158b6f04000043dbf38 \
+    --hash=sha256:3946fa46a0cf3e4c8cb1cc52f56bb536310d34f25f01ca9b6c16afa767dab110 \
+    --hash=sha256:3bec022aec2c514d9cf199522a802bd007cd588ab17ab2525f20f9c34d067c18 \
+    --hash=sha256:3c9a494bc5ec77d43cea229c4f6db1e4d8fe7e1bbffa8b6f0f0032430ff8ab44 \
+    --hash=sha256:3dce51d0f5e7951f8bb4900c257dad282f49190fdbebecd4ba99bcc41fef404d \
+    --hash=sha256:3dedcc22d73ec993f42055eff4fcfed9318d1eeb9a6606c55892a26964964e48 \
+    --hash=sha256:4042d5c8f957e15221d423ba781e85d553722fc4113f523f2feb7b188cc34c5e \
+    --hash=sha256:481551899c856c704d58119b5025793fa6730adda3571971af568f66d2424bb5 \
+    --hash=sha256:4dc1e73c36828f982bfe79fadf5919923f8a6f4df2860804db9a98c48824ce8d \
+    --hash=sha256:4e5163c14bffd570ef2affbfdd77bba66383890797df43dc8b4cc7d6f500bf53 \
+    --hash=sha256:511ef87c8aec0783e08ac18565a16d435372bc1ac25a91e6ac7f5ef2b0bff790 \
+    --hash=sha256:532bc9bf33a68613fd7d65e4b1c71a6a38d7d42604ecf239c77392e9b4e8998c \
+    --hash=sha256:54523e136b8948060c0fa0bc7b1b50c32c186f2fceee897a495406bb6e311d2b \
+    --hash=sha256:5649fd1c7bade02f320a462fdefd0b4bd3ce036065836d4f42e0de958038e116 \
+    --hash=sha256:56be790f86bfb2c98fb742ce566dfb4816e5a83384616ab59c49e0604d49c51d \
+    --hash=sha256:5b77459df20e08151cd6f8b9ef8ef1f961ef73d85c21a555c7eed5b79410ec10 \
+    --hash=sha256:5ed6ab538499c8644b8a3e18debabcd7ce684f3fa91cf867521a7a0279cab2d6 \
+    --hash=sha256:6178f72c5508bfc5fd446a5905e698c6212932f25bcdd4b47a757a50605a90e2 \
+    --hash=sha256:6370e8686f662e6a3941ee48ed4742317cafbe5707e36406e9df792cdb535776 \
+    --hash=sha256:64f02c6841d7d83f832cd97ccf8eb8a906d06eb95d5276069175c696b024b60a \
+    --hash=sha256:65bcd23054beab4d166035cabbc868a09c1a49d1efe458fe8e4361215df40265 \
+    --hash=sha256:66671f93accb62ed07da56613636f3641f1a12c13046ce91ffc923721f23c008 \
+    --hash=sha256:6696b7688f54f5af4462118f0bfa7c1621eeb87154f77fa04b9295ce7a8f2943 \
+    --hash=sha256:6785f414ae0f3c733c437e0f3929197934f526d19dfaa75e18fdb4f94c6fb374 \
+    --hash=sha256:67f6279d125ca0046a7fd386d01b311c6363844deac3e5b069b514ba3e63c246 \
+    --hash=sha256:6c114670c45346afedc0d947faf3c7f701051d2518b943679c8ff88befe14f8e \
+    --hash=sha256:6e0d51f618228538a3e8f46bd246f87a6cd030565e015803691603f55e12afb5 \
+    --hash=sha256:6ed74185b2db44f41ef35fd1617c5888e59792da9bbc9190d6c7300617182616 \
+    --hash=sha256:708838739abf24b2ceb208d0e22403dd018faeef86ddac04319a62ae884c4f15 \
+    --hash=sha256:715479b9a2802ecac752a3b0efa2b0b60285cf962ee38414211abdfccc233b41 \
+    --hash=sha256:733784b6d6def852c814bce5f318d25da2ee65dd4839a0718641c696e09a2960 \
+    --hash=sha256:750e02e074872a3fad7f233b47734166440af3cdea0add3e95163110816d6752 \
+    --hash=sha256:752a45dc4a6934060b3b0dab47e04edc3326575f82be64bc4fc293914566503e \
+    --hash=sha256:7579e913a5339fb8fa133f6bbcfd8e6749696206cf05acdbdca71a1b436d8e72 \
+    --hash=sha256:7641bb8895e77f921102f72833904dcd9901df5d6d72a2ab8f31d04b7e51e4e7 \
+    --hash=sha256:7804338df6fcc08105c7745f1502ba68d900f45fd770d5bdd5288ddccb8a42d8 \
+    --hash=sha256:80d04837f55fc81da168b98de4f4b797ef007fc8a79ab71c6ec9bc4dd662b15b \
+    --hash=sha256:813c0e0132266c08eb87469a642cb30aaff57c5f426255419572aaeceeaa7bf4 \
+    --hash=sha256:82b271f5137d07749f7bf32f70b17ab6eaabedd297e75dce75081a24f76eb545 \
+    --hash=sha256:84c018e49c3bf790f9c2771c45e9313a08c2c2a6342b162cd650258b57817706 \
+    --hash=sha256:8751d2787c9131302398b11e6c8068053dcb55d5a8964e114b6e196cf16cb366 \
+    --hash=sha256:8778f0c7a52e56f75d12dae53ae320fae900a8b9b4164b981b9c5ce059cd1fcb \
+    --hash=sha256:87fad7d9ba98c86bcb41b2dc8dbb326619be2562af1f8ff50776a39e55721c5a \
+    --hash=sha256:8d828b6667a32a728a1ad1d93957cdf37489c57b97ae6c4de2860fa749b8fc1e \
+    --hash=sha256:8e385e4267ab76874ae30db04c627faaaf0b509e1ccc11a95b3fc3e83f855c00 \
+    --hash=sha256:92a0a01ead5e668468e952e4238cccd7c537364eb7d851ab144ab6627dbbe12f \
+    --hash=sha256:94e1885b270625a9a828c9793b4d52a64445299baa1fea5a173bf1d3dd9a1a5a \
+    --hash=sha256:a180c5e59792af262bf263b21a3c49353f25945d8d9f70628e73de370d55e1e1 \
+    --hash=sha256:a277ab8928b9f299723bc1a2dabb1265911b1a76341f90a510368ca44ad9ab66 \
+    --hash=sha256:a5fe03b42827c13cdccd08e6c0247b6a6d4b5e3cdc53fd1749f5896adcdc2356 \
+    --hash=sha256:a6c5863edfbe888d9eff9c8b8087354e27618d9da76425c119293f11712a6319 \
+    --hash=sha256:a89c23ef8d2c6b27fd200a42aa4ac72786e7c60d40efdc76e6011260b6e949c4 \
+    --hash=sha256:adb2597b428735679446b46c8badf467b4ca5f5056aae4d51a19f9570301b1ad \
+    --hash=sha256:ae196f021b5e7c78e918242d217db021ed2a6ace2bc6ae94c0fc596221c7f58d \
+    --hash=sha256:ae89db9e5f98a11a4bf50407d4363e7b09b31e55bc117b4f7d80aab97ba009e5 \
+    --hash=sha256:aed52fea0513bac0ccde438c188c8a471c4e0f457c2dd20cdbf6ea7a450046c7 \
+    --hash=sha256:aef65cd602a6d0e0ff6f9930fcb1c8fec60dd2cfcb6facaf4bdb0e5873042db0 \
+    --hash=sha256:af21eb4409a119e365397b2adbaca4c9ccab56543a65d5dbd9f920d6ac29f686 \
+    --hash=sha256:b14b2d9dac08e28bb8046a1a0434b1750eb221c8f5b87a68f4fa11a6f97b5e34 \
+    --hash=sha256:bb6d88045545b26da47aa879dd4a89a71d1dce0f0e549b1abcb31dfe4a8eac49 \
+    --hash=sha256:bb8cc7534f51d9a017b93e3e85b260924f909601c3df002bcdb58ddb4dc41a5c \
+    --hash=sha256:bc17a677b21b3502a21f66a8cc64f5bfad4df8a0b8434d661666f8ce90ac3af1 \
+    --hash=sha256:bd6c2a1c7573c64738d716488d2cdd3c00e340e4835707d8fdb8dc1a66ef164e \
+    --hash=sha256:bd9b23791fe793e4968dba0c447e12f78e425c59fc0e3b97f6450f4781f3ee60 \
+    --hash=sha256:c03a41a8784091e67a39648f70c5f97b5b6a37f216896d44d2cdcb82615339a0 \
+    --hash=sha256:c0f081d69a6e58272819b70288d3221a6ee64b98df852631c80f293514d3b274 \
+    --hash=sha256:c35abb8bfff0185efac5878da64c45dafd2b37fb0383add1be155a763c1f083d \
+    --hash=sha256:c36c333c39be2dbca264d7803333c896ab8fa7d4d6f0ab7edb7dfd7aea6e98c0 \
+    --hash=sha256:c45e9440fb78f8ddabcf714b68f936737a121355bf59f3907f4e17721b9d1aae \
+    --hash=sha256:c593052c465475e64bbfe5dbd81680f64a67fdc752c56d7a0ae205dc8aeefe0f \
+    --hash=sha256:cdd68a1fb318e290a2077696b7eb7a21a49163c455979c639bf5a5dcdc46617d \
+    --hash=sha256:ce3412fbe1e31eb81ea42f4169ed94861c56e643189e1e75f0041f3fe7020abe \
+    --hash=sha256:cf1493cd8607bec4d8a7b9b004e699fcf8f9103a9284cc94962cb73d20f9d4a3 \
+    --hash=sha256:cf29836da5119f3c8a8a70667b0ef5fdca3bb12f80fd06487cfa575b3909b393 \
+    --hash=sha256:d4a48e5b3c2a489fae013b7589308a40146ee081f6f509e047e0e096084ceca1 \
+    --hash=sha256:d560742f3c0d62afaccf9f41fe485ed69bd7661a241f86a3ef0f0fb8b1a397af \
+    --hash=sha256:d6038d37043bced98a66e68d3aa2b6a35505dc01328cd65217cefe82f25def44 \
+    --hash=sha256:d61f00a0869d77422d9b2aba989e2d24afa6ffd552af442e0e58de4f35ea6d00 \
+    --hash=sha256:d635aab80466bc95771bb78d5370e74d36d1fe31467b6b29b8b57b2a3cd7d22c \
+    --hash=sha256:dca4bbc466a95ba9c0234ef56d7dd9509f63da22274589ebd4ed7f1f4d4c54e3 \
+    --hash=sha256:dd915403e231e6b1809fe9b6d9fc55cf8fb5e02765ac625d9cd623342a7905d7 \
+    --hash=sha256:e044c39e41b92c845bc815e5ae4230804e8e7bc29e399b0437d64222d92809dd \
+    --hash=sha256:e060d01aec0a910bdccb8be71faf34e7799ce36950f8294c8bf612cba65a2c9e \
+    --hash=sha256:e1421b502d83040e6d7fb2fb18dff63957f720da3d77b2fbd3187ceb63755d7b \
+    --hash=sha256:e17b8d5d6a8c47c85e68ca8379def1303fd360c3e22093a807cd34a71cd082b8 \
+    --hash=sha256:e5f4d355f0a2b1a31bc3edec6795b46324349c9cb25eed068049e4f472fb4259 \
+    --hash=sha256:e712b419df8ba5e42b226c510472b37bd57b38e897d3eca5e8cfd410a29fa859 \
+    --hash=sha256:e74327fb75de8986940def6e8dee4f127cc9752bee7355bb323cc5b2659b6d46 \
+    --hash=sha256:e80c8378d8f3d83cd3164da1ad2df9e37a666cdde7b1cb2298ed0b558064be30 \
+    --hash=sha256:e8ac484bf18ce6975760921bb6148041faa8fef0547200386ea0b52b5d27bf7b \
+    --hash=sha256:eca9705049ad3c7345d574e3510665cb2cf844c2f2dcfe675332677f081cbd46 \
+    --hash=sha256:ed065083d0898c9d5b4bbec7b026fd755ff7454e6e8b73a67f8c744b13986e24 \
+    --hash=sha256:edac0f1ab77644605be2cbba52e6b7f630731fc42b34cb0f634be1a6eface56a \
+    --hash=sha256:effc3f449787117233702311a1b7d8f59cba9ced946ba727bdc329ec69028e24 \
+    --hash=sha256:f22dec1690b584cea26fade98b2435c132c1b5f68e39f5a0b7627cd7ae31f1dc \
+    --hash=sha256:f495a1652cf3fbab2eb0639776dad966c2fb874d79d87ca07f9d5f059b8bd215 \
+    --hash=sha256:f496c9c3cc02230093d8330875c4c3cdfc3b73612a5fd921c65d39cbcef08063 \
+    --hash=sha256:f59099f9b66f0d7145115e6f80dd8b1d847176df89b234a5a6b3f00437aa0832 \
+    --hash=sha256:f59ad4c0e8f6bba240a9bb85504faa1ab438237199d4cce5f622761507b8f6a6 \
+    --hash=sha256:fbccdc05410c9ee21bbf16a35f4c1d16123dcdeb8a1d38f33654fa21d0234f79 \
+    --hash=sha256:fea24543955a6a729c45a73fe90e08c743f0b3334bbf3201e6c4bc1b0c7fa464
+    # via requests
+click==8.3.3 \
+    --hash=sha256:398329ad4837b2ff7cbe1dd166a4c0f8900c3ca3a218de04466f38f6497f18a2 \
+    --hash=sha256:a2bf429bb3033c89fa4936ffb35d5cb471e3719e1f3c8a7c3fff0b8314305613
+    # via papermill
+cloudpickle==3.1.2 \
+    --hash=sha256:7fda9eb655c9c230dab534f1983763de5835249750e85fbcef43aaa30a9a2414 \
+    --hash=sha256:9acb47f6afd73f60dc1df93bb801b472f05ff42fa6c84167d25cb206be1fbf4a
+    # via shap
+cmdstanpy==1.3.0 \
+    --hash=sha256:60b10d110993bd8345735994786b2b17782fdc5530a6adbc0cd8ec836d82c2b9 \
+    --hash=sha256:67d83fbb823948c3ca8a84912359d6c0a5c616a62025526dba5f43a1d970bc52
+    # via prophet
+colorlog==6.10.1 \
+    --hash=sha256:2d7e8348291948af66122cff006c9f8da6255d224e7cf8e37d8de2df3bad8c9c \
+    --hash=sha256:eb4ae5cb65fe7fec7773c2306061a8e63e02efc2c72eba9d27b0fa23c94f1321
+    # via optuna
+contourpy==1.3.3 \
+    --hash=sha256:023b44101dfe49d7d53932be418477dba359649246075c996866106da069af69 \
+    --hash=sha256:07ce5ed73ecdc4a03ffe3e1b3e3c1166db35ae7584be76f65dbbe28a7791b0cc \
+    --hash=sha256:083e12155b210502d0bca491432bb04d56dc3432f95a979b429f2848c3dbe880 \
+    --hash=sha256:0bf67e0e3f482cb69779dd3061b534eb35ac9b17f163d851e2a547d56dba0a3a \
+    --hash=sha256:0c1fc238306b35f246d61a1d416a627348b5cf0648648a031e14bb8705fcdfe8 \
+    --hash=sha256:13b68d6a62db8eafaebb8039218921399baf6e47bf85006fd8529f2a08ef33fc \
+    --hash=sha256:15ff10bfada4bf92ec8b31c62bf7c1834c244019b4a33095a68000d7075df470 \
+    --hash=sha256:177fb367556747a686509d6fef71d221a4b198a3905fe824430e5ea0fda54eb5 \
+    --hash=sha256:1cadd8b8969f060ba45ed7c1b714fe69185812ab43bd6b86a9123fe8f99c3263 \
+    --hash=sha256:1fd43c3be4c8e5fd6e4f2baeae35ae18176cf2e5cced681cca908addf1cdd53b \
+    --hash=sha256:22e9b1bd7a9b1d652cd77388465dc358dafcd2e217d35552424aa4f996f524f5 \
+    --hash=sha256:23416f38bfd74d5d28ab8429cc4d63fa67d5068bd711a85edb1c3fb0c3e2f381 \
+    --hash=sha256:283edd842a01e3dcd435b1c5116798d661378d83d36d337b8dde1d16a5fc9ba3 \
+    --hash=sha256:2a2a8b627d5cc6b7c41a4beff6c5ad5eb848c88255fda4a8745f7e901b32d8e4 \
+    --hash=sha256:2b7e9480ffe2b0cd2e787e4df64270e3a0440d9db8dc823312e2c940c167df7e \
+    --hash=sha256:322ab1c99b008dad206d406bb61d014cf0174df491ae9d9d0fac6a6fda4f977f \
+    --hash=sha256:33c82d0138c0a062380332c861387650c82e4cf1747aaa6938b9b6516762e772 \
+    --hash=sha256:348ac1f5d4f1d66d3322420f01d42e43122f43616e0f194fc1c9f5d830c5b286 \
+    --hash=sha256:3519428f6be58431c56581f1694ba8e50626f2dd550af225f82fb5f5814d2a42 \
+    --hash=sha256:3c30273eb2a55024ff31ba7d052dde990d7d8e5450f4bbb6e913558b3d6c2301 \
+    --hash=sha256:3d1a3799d62d45c18bafd41c5fa05120b96a28079f2393af559b843d1a966a77 \
+    --hash=sha256:451e71b5a7d597379ef572de31eeb909a87246974d960049a9848c3bc6c41bf7 \
+    --hash=sha256:459c1f020cd59fcfe6650180678a9993932d80d44ccde1fa1868977438f0b411 \
+    --hash=sha256:4d00e655fcef08aba35ec9610536bfe90267d7ab5ba944f7032549c55a146da1 \
+    --hash=sha256:4debd64f124ca62069f313a9cb86656ff087786016d76927ae2cf37846b006c9 \
+    --hash=sha256:4feffb6537d64b84877da813a5c30f1422ea5739566abf0bd18065ac040e120a \
+    --hash=sha256:50ed930df7289ff2a8d7afeb9603f8289e5704755c7e5c3bbd929c90c817164b \
+    --hash=sha256:51e79c1f7470158e838808d4a996fa9bac72c498e93d8ebe5119bc1e6becb0db \
+    --hash=sha256:556dba8fb6f5d8742f2923fe9457dbdd51e1049c4a43fd3986a0b14a1d815fc6 \
+    --hash=sha256:598c3aaece21c503615fd59c92a3598b428b2f01bfb4b8ca9c4edeecc2438620 \
+    --hash=sha256:5ed3657edf08512fc3fe81b510e35c2012fbd3081d2e26160f27ca28affec989 \
+    --hash=sha256:626d60935cf668e70a5ce6ff184fd713e9683fb458898e4249b63be9e28286ea \
+    --hash=sha256:644a6853d15b2512d67881586bd03f462c7ab755db95f16f14d7e238f2852c67 \
+    --hash=sha256:655456777ff65c2c548b7c454af9c6f33f16c8884f11083244b5819cc214f1b5 \
+    --hash=sha256:66c8a43a4f7b8df8b71ee1840e4211a3c8d93b214b213f590e18a1beca458f7d \
+    --hash=sha256:6afc576f7b33cf00996e5c1102dc2a8f7cc89e39c0b55df93a0b78c1bd992b36 \
+    --hash=sha256:6c3d53c796f8647d6deb1abe867daeb66dcc8a97e8455efa729516b997b8ed99 \
+    --hash=sha256:709a48ef9a690e1343202916450bc48b9e51c049b089c7f79a267b46cffcdaa1 \
+    --hash=sha256:70f9aad7de812d6541d29d2bbf8feb22ff7e1c299523db288004e3157ff4674e \
+    --hash=sha256:8153b8bfc11e1e4d75bcb0bff1db232f9e10b274e0929de9d608027e0d34ff8b \
+    --hash=sha256:87acf5963fc2b34825e5b6b048f40e3635dd547f590b04d2ab317c2619ef7ae8 \
+    --hash=sha256:88df9880d507169449d434c293467418b9f6cbe82edd19284aa0409e7fdb933d \
+    --hash=sha256:929ddf8c4c7f348e4c0a5a3a714b5c8542ffaa8c22954862a46ca1813b667ee7 \
+    --hash=sha256:92d9abc807cf7d0e047b95ca5d957cf4792fcd04e920ca70d48add15c1a90ea7 \
+    --hash=sha256:95b181891b4c71de4bb404c6621e7e2390745f887f2a026b2d99e92c17892339 \
+    --hash=sha256:9e999574eddae35f1312c2b4b717b7885d4edd6cb46700e04f7f02db454e67c1 \
+    --hash=sha256:a15459b0f4615b00bbd1e91f1b9e19b7e63aea7483d03d804186f278c0af2659 \
+    --hash=sha256:a22738912262aa3e254e4f3cb079a95a67132fc5a063890e224393596902f5a4 \
+    --hash=sha256:ab2fd90904c503739a75b7c8c5c01160130ba67944a7b77bbf36ef8054576e7f \
+    --hash=sha256:ab3074b48c4e2cf1a960e6bbeb7f04566bf36b1861d5c9d4d8ac04b82e38ba20 \
+    --hash=sha256:afe5a512f31ee6bd7d0dda52ec9864c984ca3d66664444f2d72e0dc4eb832e36 \
+    --hash=sha256:b08a32ea2f8e42cf1d4be3169a98dd4be32bafe4f22b6c4cb4ba810fa9e5d2cb \
+    --hash=sha256:b20c7c9a3bf701366556e1b1984ed2d0cedf999903c51311417cf5f591d8c78d \
+    --hash=sha256:b2e8faa0ed68cb29af51edd8e24798bb661eac3bd9f65420c1887b6ca89987c8 \
+    --hash=sha256:b7301b89040075c30e5768810bc96a8e8d78085b47d8be6e4c3f5a0b4ed478a0 \
+    --hash=sha256:b7448cb5a725bb1e35ce88771b86fba35ef418952474492cf7c764059933ff8b \
+    --hash=sha256:ca0fdcd73925568ca027e0b17ab07aad764be4706d0a925b89227e447d9737b7 \
+    --hash=sha256:ca658cd1a680a5c9ea96dc61cdbae1e85c8f25849843aa799dfd3cb370ad4fbe \
+    --hash=sha256:cbedb772ed74ff5be440fa8eee9bd49f64f6e3fc09436d9c7d8f1c287b121d77 \
+    --hash=sha256:cd5dfcaeb10f7b7f9dc8941717c6c2ade08f587be2226222c12b25f0483ed497 \
+    --hash=sha256:cf9022ef053f2694e31d630feaacb21ea24224be1c3ad0520b13d844274614fd \
+    --hash=sha256:d002b6f00d73d69333dac9d0b8d5e84d9724ff9ef044fd63c5986e62b7c9e1b1 \
+    --hash=sha256:d06bb1f751ba5d417047db62bca3c8fde202b8c11fb50742ab3ab962c81e8216 \
+    --hash=sha256:d304906ecc71672e9c89e87c4675dc5c2645e1f4269a5063b99b0bb29f232d13 \
+    --hash=sha256:e4e6b05a45525357e382909a4c1600444e2a45b4795163d3b22669285591c1ae \
+    --hash=sha256:e74a9a0f5e3fff48fb5a7f2fd2b9b70a3fe014a67522f79b7cca4c0c7e43c9ae \
+    --hash=sha256:ea37e7b45949df430fe649e5de8351c423430046a2af20b1c1961cae3afcda77 \
+    --hash=sha256:f64836de09927cba6f79dcd00fdd7d5329f3fccc633468507079c829ca4db4e3 \
+    --hash=sha256:fd6ec6be509c787f1caf6b247f0b1ca598bef13f4ddeaa126b7658215529ba0f \
+    --hash=sha256:fd907ae12cd483cd83e414b12941c632a969171bf90fc937d0c9f268a31cafff \
+    --hash=sha256:fd914713266421b7536de2bfa8181aa8c699432b6763a0ea64195ebe28bff6a9 \
+    --hash=sha256:fde6c716d51c04b1c25d0b90364d0be954624a0ee9d60e23e850e8d48353d07a
+    # via matplotlib
+cycler==0.12.1 \
+    --hash=sha256:85cef7cff222d8644161529808465972e51340599459b8ac3ccbac5a854e0d30 \
+    --hash=sha256:88bb128f02ba341da8ef447245a9e138fae777f6a23943da4540077d3601eb1c
+    # via matplotlib
+cython==3.2.4 \
+    --hash=sha256:02cb0cc0f23b9874ad262d7d2b9560aed9c7e2df07b49b920bda6f2cc9cb505e \
+    --hash=sha256:03893c88299a2c868bb741ba6513357acd104e7c42265809fd58dce1456a36fc \
+    --hash=sha256:14dae483ca2838b287085ff98bc206abd7a597b7bb16939a092f8e84d9062842 \
+    --hash=sha256:1a64a112a34ec719b47c01395647e54fb4cf088a511613f9a3a5196694e8e382 \
+    --hash=sha256:28b1e363b024c4b8dcf52ff68125e635cb9cb4b0ba997d628f25e32543a71103 \
+    --hash=sha256:28e8075087a59756f2d059273184b8b639fe0f16cf17470bd91c39921bc154e0 \
+    --hash=sha256:2b1f12c0e4798293d2754e73cd6f35fa5bbdf072bdc14bc6fc442c059ef2d290 \
+    --hash=sha256:31a90b4a2c47bb6d56baeb926948348ec968e932c1ae2c53239164e3e8880ccf \
+    --hash=sha256:35ab0632186057406ec729374c737c37051d2eacad9d515d94e5a3b3e58a9b02 \
+    --hash=sha256:36bf3f5eb56d5281aafabecbaa6ed288bc11db87547bba4e1e52943ae6961ccf \
+    --hash=sha256:3b6e58f73a69230218d5381817850ce6d0da5bb7e87eb7d528c7027cbba40b06 \
+    --hash=sha256:3b8e62049afef9da931d55de82d8f46c9a147313b69d5ff6af6e9121d545ce7a \
+    --hash=sha256:55b6c44cd30821f0b25220ceba6fe636ede48981d2a41b9bbfe3c7902ce44ea7 \
+    --hash=sha256:55eb425c0baf1c8a46aa4424bc35b709db22f3c8a1de33adb3ecb8a3d54ea42a \
+    --hash=sha256:64d7f71be3dd6d6d4a4c575bb3a4674ea06d1e1e5e4cd1b9882a2bc40ed3c4c9 \
+    --hash=sha256:67922c9de058a0bfb72d2e75222c52d09395614108c68a76d9800f150296ddb3 \
+    --hash=sha256:6d5267f22b6451eb1e2e1b88f6f78a2c9c8733a6ddefd4520d3968d26b824581 \
+    --hash=sha256:72e6c0bbd978e2678b45351395f6825b9b8466095402eae293f4f7a73e9a3e85 \
+    --hash=sha256:732fc93bc33ae4b14f6afaca663b916c2fdd5dcbfad7114e17fb2434eeaea45c \
+    --hash=sha256:767b143704bdd08a563153448955935844e53b852e54afdc552b43902ed1e235 \
+    --hash=sha256:83266c356c13c68ffe658b4905279c993d8a5337bb0160fa90c8a3e297ea9a2e \
+    --hash=sha256:84226ecd313b233da27dc2eb3601b4f222b8209c3a7216d8733b031da1dc64e6 \
+    --hash=sha256:869487ea41d004f8b92171f42271fbfadb1ec03bede3158705d16cd570d6b891 \
+    --hash=sha256:90f43be4eaa6afd58ce20d970bb1657a3627c44e1760630b82aa256ba74b4acb \
+    --hash=sha256:983f9d2bb8a896e16fa68f2b37866ded35fa980195eefe62f764ddc5f9f5ef8e \
+    --hash=sha256:b362819d155fff1482575e804e43e3a8825332d32baa15245f4642022664a3f4 \
+    --hash=sha256:b84d4e3c875915545f77c88dba65ad3741afd2431e5cdee6c9a20cefe6905647 \
+    --hash=sha256:ca2399dc75796b785f74fb85c938254fa10c80272004d573c455f9123eceed86 \
+    --hash=sha256:ca578c9cb872c7ecffbe14815dc4590a003bc13339e90b2633540c7e1a252839 \
+    --hash=sha256:d4b4fd5332ab093131fa6172e8362f16adef3eac3179fd24bbdc392531cb82fa \
+    --hash=sha256:e3b5ac54e95f034bc7fb07313996d27cbf71abc17b229b186c1540942d2dc28e \
+    --hash=sha256:e65e4773021f8dc8532010b4fbebe782c77f9a0817e93886e518c93bd6a44e9d \
+    --hash=sha256:e71efb20048358a6b8ec604a0532961c50c067b5e63e345e2e359fff72feaee8 \
+    --hash=sha256:f136f379a4a54246facd0eb6f1ee15c3837cb314ce87b677582ec014db4c6845 \
+    --hash=sha256:f583cad7a7eed109f0babb5035e92d0c1260598f53add626a8568b57246b62c3 \
+    --hash=sha256:f81eda419b5ada7b197bbc3c5f4494090e3884521ffd75a3876c93fbf66c9ca8 \
+    --hash=sha256:f8d685a70bce39acc1d62ec3916d9b724b5ef665b0ce25ae55e1c85ee09747fc \
+    --hash=sha256:fdfdd753ad7e18e5092b413e9f542e8d28b8a08203126090e1c15f7783b7fe57 \
+    --hash=sha256:ff9af2134c05e3734064808db95b4dd7341a39af06e8945d05ea358e1741aaed
+    # via pmdarima
+distlib==0.4.0 \
+    --hash=sha256:9659f7d87e46584a30b5780e43ac7a2143098441670ff0a49d5f9034c54a6c16 \
+    --hash=sha256:feec40075be03a04501a973d81f633735b4b69f98b05450592310c0f401a4e0d
+    # via virtualenv
+duckdb==1.5.2 \
+    --hash=sha256:0b291786014df1133f8f18b9df4d004484613146e858d71a21791e0fcca16cf4 \
+    --hash=sha256:2323c1195c10fb2bb982fc0218c730b43d1b92a355d61e68e3c5f3ac9d44c34f \
+    --hash=sha256:2a1de4f4d454b8c97aec546c82003fc834d3422ce4bc6a19902f3462ef293bed \
+    --hash=sha256:35579b8e3a064b5eaf15b0eafc558056a13f79a0a62e34cc4baf57119daecfec \
+    --hash=sha256:376856066c65ccd55fcb3a380bbe33a71ce089fc4623d229ffc6e82251afdb6d \
+    --hash=sha256:411ad438bd4140f189a10e7f515781335962c5d18bd07837dc6d202e3985253d \
+    --hash=sha256:4420b3f47027a7849d0e1815532007f377fa95ee5810b47ea717d35525c12f79 \
+    --hash=sha256:486c862bf7f163c0110b6d85b3e5c031d224a671cca468f12ebb1d3a348f6b39 \
+    --hash=sha256:52a21823f3fbb52f0f0e5425e20b07391ad882464b955879499b5ff0b45a376b \
+    --hash=sha256:5596bbfc31b1b259db69c8d847b42d036ce2c4804f9ccb28f9fc46a16de7bc53 \
+    --hash=sha256:56d38b3c4e0ef2abb58898d0fd423933999ed535c45e75e9d9f72e1d5fed69b8 \
+    --hash=sha256:638da0d5102b6cb6f7d47f83d0600708ac1d3cb46c5e9aaabc845f9ba4d69246 \
+    --hash=sha256:63bf8687feefeed51adf45fa3b062ab8b1b1c350492b7518491b86bae68b1da1 \
+    --hash=sha256:6b0fe75c148000f060aa1a27b293cacc0ea08cc1cad724fbf2143d56070a3785 \
+    --hash=sha256:70631c847ca918ee710ec874241b00cf9d2e5be90762cbb2a0389f17823c08f7 \
+    --hash=sha256:7f69164b048e498b9e9140a24343108a5ae5f17bfb3485185f55fdf9b1aa924d \
+    --hash=sha256:81fc4fbf0b5e25840b39ba2a10b78c6953c0314d5d0434191e7898f34ab1bba3 \
+    --hash=sha256:84b193aca20565dedb3172de15f843c659c3a6c773bf14843a9bd781c850e7db \
+    --hash=sha256:8d599758b4e48bf12e18c9b960cf491d219f0c4972d19a45489c05cc5ab36f83 \
+    --hash=sha256:8dbd7e31e5dc157bfe8803fa7d2652336265c6c19926c5a4a9b40f8222868d08 \
+    --hash=sha256:98c0535cd6d901f61a5ea3c2e26a1fd28482953d794deb183daf568e3aa5dda6 \
+    --hash=sha256:a9cd5e71702d446613750405cde03f66ed268f4c321da071b0472759dad19536 \
+    --hash=sha256:bb42e6ed543902e14eae647850da24103a89f0bc2587dec5601b1c1f213bd2ed \
+    --hash=sha256:be37680ddb380015cb37318e378c53511c45c4f0d8fac5599d22b7d092b9217a \
+    --hash=sha256:c69907354ffee94ba8cf782daf0480dab7557f21ce27fffa6c0ea8f74ed4b8e2 \
+    --hash=sha256:c99ef73a277c8921bc0a1f16dee38d924484251d9cfd20951748c20fcd5ed855 \
+    --hash=sha256:c9f3e0b71b8a50fccfb42794899285d9d318ce2503782b9dd54868e5ecd0ad31 \
+    --hash=sha256:ce0b8141a10d37ecef729c45bc41d334854013f4389f1488bd6035c5579aaac1 \
+    --hash=sha256:ce17670bb392ea1b3650537db02bd720908776b5b95f6d2472d31a7de59d1dc1 \
+    --hash=sha256:d72b8856b1839d35648f38301b058f6232f4d36b463fe4dc8f4d3fdff2df1a2e \
+    --hash=sha256:d9b4f5430bf4f05d4c0dc4c55c75def3a5af4be0343be20fa2bfc577343fbfc9 \
+    --hash=sha256:e6495b00cad16888384119842797c49316a96ae1cb132bb03856d980d95afee1 \
+    --hash=sha256:ea58ff5b0880593a280cf5511734b17711b32ee1f58b47d726e8600848358160 \
+    --hash=sha256:ef461bca07313412dc09961c4a4757a851f56b95ac01c58fac6007632b7b94f2 \
+    --hash=sha256:fc85a5dbcbe6eccac1113c72370d1d3aacfdd49198d63950bdf7d8638a307f00
+    # via -r requirements.in
+entrypoints==0.4 \
+    --hash=sha256:b706eddaa9218a19ebcd67b56818f05bb27589b1ca9e8d797b74affad4ccacd4 \
+    --hash=sha256:f174b5ff827504fd3cd97cc3f8649f3693f51538c7e4bdf3ef002c8429d42f9f
+    # via papermill
+fastjsonschema==2.21.2 \
+    --hash=sha256:1c797122d0a86c5cace2e54bf4e819c36223b552017172f32c5c024a6b77e463 \
+    --hash=sha256:b1eb43748041c880796cd077f1a07c3d94e93ae84bba5ed36800a33554ae05de
+    # via nbformat
+filelock==3.29.0 \
+    --hash=sha256:69974355e960702e789734cb4871f884ea6fe50bd8404051a3530bc07809cf90 \
+    --hash=sha256:96f5f6344709aa1572bbf631c640e4ebeeb519e08da902c39a001882f30ac258
+    # via
+    #   python-discovery
+    #   virtualenv
+flatbuffers==25.12.19 \
+    --hash=sha256:7634f50c427838bb021c2d66a3d1168e9d199b0607e6329399f04846d42e20b4
+    # via onnxruntime
+fonttools==4.62.1 \
+    --hash=sha256:0aa72c43a601cfa9273bb1ae0518f1acadc01ee181a6fc60cd758d7fdadffc04 \
+    --hash=sha256:0b3ae47e8636156a9accff64c02c0924cbebad62854c4a6dbdc110cd5b4b341a \
+    --hash=sha256:12859ff0b47dd20f110804c3e0d0970f7b832f561630cd879969011541a464a9 \
+    --hash=sha256:149f7d84afca659d1a97e39a4778794a2f83bf344c5ee5134e09995086cc2392 \
+    --hash=sha256:1596aeaddf7f78e21e68293c011316a25267b3effdaccaf4d59bc9159d681b82 \
+    --hash=sha256:19177c8d96c7c36359266e571c5173bcee9157b59cfc8cb0153c5673dc5a3a7d \
+    --hash=sha256:1c5c25671ce8805e0d080e2ffdeca7f1e86778c5cbfbeae86d7f866d8830517b \
+    --hash=sha256:1eecc128c86c552fb963fe846ca4e011b1be053728f798185a1687502f6d398e \
+    --hash=sha256:268abb1cb221e66c014acc234e872b7870d8b5d4657a83a8f4205094c32d2416 \
+    --hash=sha256:2d850f66830a27b0d498ee05adb13a3781637b1826982cd7e2b3789ef0cc71ae \
+    --hash=sha256:2e7abd2b1e11736f58c1de27819e1955a53267c21732e78243fa2fa2e5c1e069 \
+    --hash=sha256:403d28ce06ebfc547fbcb0cb8b7f7cc2f7a2d3e1a67ba9a34b14632df9e080f9 \
+    --hash=sha256:40975849bac44fb0b9253d77420c6d8b523ac4dcdcefeff6e4d706838a5b80f7 \
+    --hash=sha256:486f32c8047ccd05652aba17e4a8819a3a9d78570eb8a0e3b4503142947880ed \
+    --hash=sha256:49a445d2f544ce4a69338694cad575ba97b9a75fff02720da0882d1a73f12800 \
+    --hash=sha256:59b372b4f0e113d3746b88985f1c796e7bf830dd54b28374cd85c2b8acd7583e \
+    --hash=sha256:5a648bde915fba9da05ae98856987ca91ba832949a9e2888b48c47ef8b96c5a9 \
+    --hash=sha256:5f37df1cac61d906e7b836abe356bc2f34c99d4477467755c216b72aa3dc748b \
+    --hash=sha256:6706d1cb1d5e6251a97ad3c1b9347505c5615c112e66047abbef0f8545fa30d1 \
+    --hash=sha256:68959f5fc58ed4599b44aad161c2837477d7f35f5f79402d97439974faebfebe \
+    --hash=sha256:6acb4109f8bee00fec985c8c7afb02299e35e9c94b57287f3ea542f28bd0b0a7 \
+    --hash=sha256:7487782e2113861f4ddcc07c3436450659e3caa5e470b27dc2177cade2d8e7fd \
+    --hash=sha256:7aa21ff53e28a9c2157acbc44e5b401149d3c9178107130e82d74ceb500e5056 \
+    --hash=sha256:7bca7a1c1faf235ffe25d4f2e555246b4750220b38de8261d94ebc5ce8a23c23 \
+    --hash=sha256:8d337fdd49a79b0d51c4da87bc38169d21c3abbf0c1aa9367eff5c6656fb6dae \
+    --hash=sha256:8f8fca95d3bb3208f59626a4b0ea6e526ee51f5a8ad5d91821c165903e8d9260 \
+    --hash=sha256:90365821debbd7db678809c7491ca4acd1e0779b9624cdc6ddaf1f31992bf974 \
+    --hash=sha256:92bb00a947e666169c99b43753c4305fc95a890a60ef3aeb2a6963e07902cc87 \
+    --hash=sha256:93c316e0f5301b2adbe6a5f658634307c096fd5aae60a5b3412e4f3e1728ab24 \
+    --hash=sha256:942b03094d7edbb99bdf1ae7e9090898cad7bf9030b3d21f33d7072dbcb51a53 \
+    --hash=sha256:9c125ffa00c3d9003cdaaf7f2c79e6e535628093e14b5de1dccb08859b680936 \
+    --hash=sha256:9dde91633f77fa576879a0c76b1d89de373cae751a98ddf0109d54e173b40f14 \
+    --hash=sha256:9e7863e10b3de72376280b515d35b14f5eeed639d1aa7824f4cf06779ec65e42 \
+    --hash=sha256:a24decd24d60744ee8b4679d38e88b8303d86772053afc29b19d23bb8207803c \
+    --hash=sha256:a5d8825e1140f04e6c99bb7d37a9e31c172f3bc208afbe02175339e699c710e1 \
+    --hash=sha256:aa69d10ed420d8121118e628ad47d86e4caa79ba37f968597b958f6cceab7eca \
+    --hash=sha256:ad5cca75776cd453b1b035b530e943334957ae152a36a88a320e779d61fc980c \
+    --hash=sha256:b4e0fcf265ad26e487c56cb12a42dffe7162de708762db951e1b3f755319507d \
+    --hash=sha256:b820fcb92d4655513d8402d5b219f94481c4443d825b4372c75a2072aa4b357a \
+    --hash=sha256:bd13b7999d59c5eb1c2b442eb2d0c427cb517a0b7a1f5798fc5c9e003f5ff782 \
+    --hash=sha256:bdfe592802ef939a0e33106ea4a318eeb17822c7ee168c290273cbd5fabd746c \
+    --hash=sha256:c05557a78f8fa514da0f869556eeda40887a8abc77c76ee3f74cf241778afd5a \
+    --hash=sha256:c22b1014017111c401469e3acc5433e6acf6ebcc6aa9efb538a533c800971c79 \
+    --hash=sha256:c9b9e288b4da2f64fd6180644221749de651703e8d0c16bd4b719533a3a7d6e3 \
+    --hash=sha256:d241cdc4a67b5431c6d7f115fdf63335222414995e3a1df1a41e1182acd4bcc7 \
+    --hash=sha256:e54c75fd6041f1122476776880f7c3c3295ffa31962dc6ebe2543c00dca58b5d \
+    --hash=sha256:e8514f4924375f77084e81467e63238b095abda5107620f49421c368a6017ed2 \
+    --hash=sha256:ee91628c08e76f77b533d65feb3fbe6d9dad699f95be51cf0d022db94089cdc4 \
+    --hash=sha256:ef46db46c9447103b8f3ff91e8ba009d5fe181b1920a83757a5762551e32bb68 \
+    --hash=sha256:fa1d16210b6b10a826d71bed68dd9ec24a9e218d5a5e2797f37c573e7ec215ca
+    # via matplotlib
+greenlet==3.5.0 \
+    --hash=sha256:0ecec963079cd58cbd14723582384f11f166fd58883c15dcbfb342e0bc9b5846 \
+    --hash=sha256:0ed006e4b86c59de7467eb2601cd1b77b5a7d657d1ee55e30fe30d76451edba4 \
+    --hash=sha256:0ff251e9a0279522e62f6176412869395a64ddf2b5c5f782ff609a8216a4e662 \
+    --hash=sha256:1aa4ce8debcd4ea7fb2e150f3036588c41493d1d52c43538924ae1819003f4ce \
+    --hash=sha256:1bae92a1dd94c5f9d9493c3a212dd874c202442047cf96446412c862feca83a2 \
+    --hash=sha256:1eb67d5adefb5bd2e182d42678a328979a209e4e82eb93575708185d31d1f588 \
+    --hash=sha256:2094acd54b272cb6eae8c03dd87b3fa1820a4cef18d6889c378d503500a1dc13 \
+    --hash=sha256:2628d6c86f6cb0cb45e0c3c54058bbec559f57eaae699447748cb3928150577e \
+    --hash=sha256:29ea813b2e1f45fa9649a17853b2b5465c4072fbcb072e5af6cd3a288216574a \
+    --hash=sha256:362624e6a8e5bca3b8233e45eef33903a100e9539a2b995c364d595dbc4018b3 \
+    --hash=sha256:3a717fbc46d8a354fa675f7c1e813485b6ba3885f9bef0cd56e5ba27d758ff5b \
+    --hash=sha256:3bc59be3945ae9750b9e7d45067d01ae3fe90ea5f9ade99239dabdd6e28a5033 \
+    --hash=sha256:3ec9ea74e7268ace7f9aab1b1a4e730193fc661b39a993cd91c606c32d4a3628 \
+    --hash=sha256:41353ec2ecedf7aa8f682753a41919f8718031a6edac46b8d3dc7ed9e1ceb136 \
+    --hash=sha256:47422135b1d308c14b2c6e758beedb1acd33bb91679f5670edf77bf46244722b \
+    --hash=sha256:4964101b8585c144cbda5532b1aa644255126c08a265dae90c16e7a0e63aaa9d \
+    --hash=sha256:4a448128607be0de65342dc9b31be7f948ef4cc0bc8832069350abefd310a8f2 \
+    --hash=sha256:4b28037cb07768933c54d81bfe47a85f9f402f57d7d69743b991a713b63954eb \
+    --hash=sha256:4d0eadc7e4d9ffb2af4247b606cae307be8e448911e5a0d0b16d72fc3d224cfd \
+    --hash=sha256:54d243512da35485fc7a6bf3c178fdda6327a9d6506fcdd62b1abd1e41b2927b \
+    --hash=sha256:55fa7ea52771be44af0de27d8b80c02cd18c2c3cddde6c847ecebdf72418b6a1 \
+    --hash=sha256:57a43c6079a89713522bc4bcb9f75070ecf5d3dbad7792bfe42239362cbf2a16 \
+    --hash=sha256:58c1c374fe2b3d852f9b6b11a7dff4c85404e51b9a596fd9e89cf904eb09866d \
+    --hash=sha256:5a5ed18de6a0f6cc7087f1563f6bd93fc7df1c19165ca01e9bde5a5dc281d106 \
+    --hash=sha256:5e05ba267789ea87b5a155cf0e810b1ab88bf18e9e8740813945ceb8ee4350ba \
+    --hash=sha256:5ecd83806b0f4c2f53b1018e0005cd82269ea01d42befc0368730028d850ed1c \
+    --hash=sha256:64d6ac45f7271f48e45f67c95b54ef73534c52ec041fcda8edf520c6d811f4bc \
+    --hash=sha256:680bd0e7ad5e8daa8a4aa89f68fd6adc834b8a8036dc256533f7e08f4a4b01f7 \
+    --hash=sha256:6c18dfb59c70f5a94acd271c72e90128c3c776e41e5f07767908c8c1b74ad339 \
+    --hash=sha256:6d874e79afd41a96e11ff4c5d0bc90a80973e476fda1c2c64985667397df432b \
+    --hash=sha256:7022615368890680e67b9965d33f5773aade330d5343bbe25560135aaa849eae \
+    --hash=sha256:703cb211b820dbffbbc55a16bfc6e4583a6e6e990f33a119d2cc8b83211119c8 \
+    --hash=sha256:728a73687e39ae9ca34e4694cbf2f049d3fbc7174639468d0f67200a97d8f9e2 \
+    --hash=sha256:728d9667d8f2f586644b748dbd9bb67e50d6a9381767d1357714ea6825bb3bf5 \
+    --hash=sha256:762612baf1161ccb8437c0161c668a688223cba28e1bf038f4eb47b13e39ccdf \
+    --hash=sha256:7fc391b1566f2907d17aaebe78f8855dc45675159a775fcf9e61f8ee0078e87f \
+    --hash=sha256:804a70b328e706b785c6ef16187051c394a63dd1a906d89be24b6ad77759f13f \
+    --hash=sha256:83ed9f27f1680b50e89f40f6df348a290ea234b249a4003d366663a12eab94f2 \
+    --hash=sha256:884f649de075b84739713d41dd4dfd41e2b910bfb769c4a3ea02ec1da52cd9bb \
+    --hash=sha256:8f1cc966c126639cd152fdaa52624d2655f492faa79e013fea161de3e6dda082 \
+    --hash=sha256:8f52a464e4ed91780bdfbbdd2b97197f3accaa629b98c200f4dffada759f3ae7 \
+    --hash=sha256:9c615f869163e14bb1ced20322d8038fb680b08236521ac3f30cd4c1288785a0 \
+    --hash=sha256:9d280a7f5c331622c69f97eb167f33577ff2d1df282c41cd15907fc0a3ca198c \
+    --hash=sha256:a10a732421ab4fec934783ce3e54763470d0181db6e3468f9103a275c3ed1853 \
+    --hash=sha256:a96fcee45e03fe30a62669fd16ab5c9d3c172660d3085605cb1e2d1280d3c988 \
+    --hash=sha256:a97e4821aa710603f94de0da25f25096454d78ffdace5dc77f3a006bc01abba3 \
+    --hash=sha256:ba8f0bdc2fae6ce915dfd0c16d2d00bca7e4247c1eae4416e06430e522137858 \
+    --hash=sha256:bf2d8a80bec89ab46221ae45c5373d5ba0bd36c19aa8508e85c6cd7e5106cd37 \
+    --hash=sha256:cda05425526240807408156b6960a17a79a0c760b813573b67027823be760977 \
+    --hash=sha256:d419647372241bc68e957bf38d5c1f98852155e4146bd1e4121adea81f4f01e4 \
+    --hash=sha256:d4d9f0624c775f2dfc56ba54d515a8c771044346852a918b405914f6b19d7fd8 \
+    --hash=sha256:d60097128cb0a1cab9ea541186ea13cd7b847b8449a7787c2e2350da0cb82d86 \
+    --hash=sha256:db2910d3c809444e0a20147361f343fe2798e106af8d9d8506f5305302655a9f \
+    --hash=sha256:ddb36c7d6c9c0a65f18c7258634e0c416c6ab59caac8c987b96f80c2ebda0112 \
+    --hash=sha256:ddc090c5c1792b10246a78e8c2163ebbe04cf877f9d785c230a7b27b39ad038e \
+    --hash=sha256:e5ddf316ced87539144621453c3aef229575825fe60c604e62bedc4003f372b2 \
+    --hash=sha256:f35807464c4c58c55f0d31dfa83c541a5615d825c2fe3d2b95360cf7c4e3c0a8 \
+    --hash=sha256:f8c30c2225f40dd76c50790f0eb3b5c7c18431efb299e2782083e1981feed243 \
+    --hash=sha256:fa94cb2288681e3a11645958f1871d48ee9211bd2f66628fdace505927d6e564
+    # via sqlalchemy
+holidays==0.95 \
+    --hash=sha256:3b79fdd141cbc740526a5184d1cd41fd264fac4aba383554359d4bb6d52937d3 \
+    --hash=sha256:5a204ff6d2ac2fff82fb5ca2a55dbbf265c2f952ca225c16b9ce12755664256d
+    # via prophet
+identify==2.6.19 \
+    --hash=sha256:20e6a87f786f768c092a721ad107fc9df0eb89347be9396cadf3f4abbd1fb78a \
+    --hash=sha256:6be5020c38fcb07da56c53733538a3081ea5aa70d36a156f83044bfbf9173842
+    # via pre-commit
+idna==3.13 \
+    --hash=sha256:585ea8fe5d69b9181ec1afba340451fba6ba764af97026f92a91d4eef164a242 \
+    --hash=sha256:892ea0cde124a99ce773decba204c5552b69c3c67ffd5f232eb7696135bc8bb3
+    # via requests
+importlib-resources==7.1.0 \
+    --hash=sha256:0722d4c6212489c530f2a145a34c0a7a3b4721bc96a15fada5930e2a0b760708 \
+    --hash=sha256:1bd7b48b4088eddb2cd16382150bb515af0bd2c70128194392725f82ad2c96a1
+    # via prophet
+iniconfig==2.3.0 \
+    --hash=sha256:c76315c77db068650d49c5b56314774a7804df16fee4402c1f19d6d15d8c4730 \
+    --hash=sha256:f631c04d2c48c52b84d0d0549c99ff3859c98df65b3101406327ecc7d53fbf12
+    # via pytest
+jinja2==3.1.6 \
+    --hash=sha256:0137fb05990d35f1275a587e9aee6d56da821fc83491a0fb838183be43f66d6d \
+    --hash=sha256:85ece4451f492d0c13c5dd7c13a64681a86afae63a5f347908daf103ce6d2f67
+    # via -r requirements.in
+joblib==1.5.3 \
+    --hash=sha256:5fc3c5039fc5ca8c0276333a188bbd59d6b7ab37fe6632daa76bc7f9ec18e713 \
+    --hash=sha256:8561a3269e6801106863fd0d6d84bb737be9e7631e33aaed3fb9ce5953688da3
+    # via
+    #   pmdarima
+    #   pynndescent
+    #   scikit-learn
+jsonschema==4.26.0 \
+    --hash=sha256:0c26707e2efad8aa1bfc5b7ce170f3fccc2e4918ff85989ba9ffa9facb2be326 \
+    --hash=sha256:d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce
+    # via nbformat
+jsonschema-specifications==2025.9.1 \
+    --hash=sha256:98802fee3a11ee76ecaca44429fda8a41bff98b00a0f2838151b113f210cc6fe \
+    --hash=sha256:b540987f239e745613c7a9176f3edb72b832a4ac465cf02712288397832b5e8d
+    # via jsonschema
+jupyter-client==8.8.0 \
+    --hash=sha256:d556811419a4f2d96c869af34e854e3f059b7cc2d6d01a9cd9c85c267691be3e \
+    --hash=sha256:f93a5b99c5e23a507b773d3a1136bd6e16c67883ccdbd9a829b0bbdb98cd7d7a
+    # via nbclient
+jupyter-core==5.9.1 \
+    --hash=sha256:4d09aaff303b9566c3ce657f580bd089ff5c91f5f89cf7d8846c3cdf465b5508 \
+    --hash=sha256:ebf87fdc6073d142e114c72c9e29a9d7ca03fad818c5d300ce2adc1fb0743407
+    # via
+    #   jupyter-client
+    #   nbclient
+    #   nbformat
+jupytext==1.19.1 \
+    --hash=sha256:82587c07e299173c70ed5e8ec7e75183edf1be289ed518bab49ad0d4e3d5f433 \
+    --hash=sha256:d8975035155d034bdfde5c0c37891425314b7ea8d3a6c4b5d18c294348714cd9
+    # via kaggle
+kaggle==2.1.0 \
+    --hash=sha256:bd120b5689cc8e00a9c1d35c0ead6bde58084a009787b9f5b5414f1d9c67825f \
+    --hash=sha256:cae0c080e7366ce9da5b92f58fe616d9e230df18827573afbb7e3067eb752e64
+    # via -r requirements.in
+kagglesdk==0.1.22 \
+    --hash=sha256:33ff680b4dbc65fd33352723877b996e1a8900a5a787e9af065757dec492239f \
+    --hash=sha256:8d051a1d3fe9bbe5c095ade43a9e7eb3511cf5bee1999054f759801c6e1350a9
+    # via kaggle
+kiwisolver==1.5.0 \
+    --hash=sha256:012b1eb16e28718fa782b5e61dc6f2da1f0792ca73bd05d54de6cb9561665fc9 \
+    --hash=sha256:01808c6d15f4c3e8559595d6d1fe6411c68e4a3822b4b9972b44473b24f4e679 \
+    --hash=sha256:0255a027391d52944eae1dbb5d4cc5903f57092f3674e8e544cdd2622826b3f0 \
+    --hash=sha256:0b85aad90cea8ac6797a53b5d5f2e967334fa4d1149f031c4537569972596cb8 \
+    --hash=sha256:0bf3acf1419fa93064a4c2189ac0b58e3be7872bf6ee6177b0d4c63dc4cea276 \
+    --hash=sha256:0c50b89ffd3e1a911c69a1dd3de7173c0cd10b130f56222e57898683841e4f96 \
+    --hash=sha256:0cbe94b69b819209a62cb27bdfa5dc2a8977d8de2f89dfd97ba4f53ed3af754e \
+    --hash=sha256:0df54df7e686afa55e6f21fb86195224a6d9beb71d637e8d7920c95cf0f89aac \
+    --hash=sha256:0e3aafb33aed7479377e5e9a82e9d4bf87063741fc99fc7ae48b0f16e32bdd6f \
+    --hash=sha256:12e91c215a96e39f57989c8912ae761286ac5a9584d04030ceb3368a357f017a \
+    --hash=sha256:1465387ac63576c3e125e5337a6892b9e99e0627d52317f3ca79e6930d889d15 \
+    --hash=sha256:16b85d37c2cbb3253226d26e64663f755d88a03439a9c47df6246b35defbdfb7 \
+    --hash=sha256:1b0feb50971481a2cc44d94e88bdb02cdd497618252ae226b8eb1201b957e368 \
+    --hash=sha256:1d49a49ac4cbfb7c1375301cd1ec90169dfeae55ff84710d782260ce77a75a02 \
+    --hash=sha256:1d9daea4ea6b9be74fe2f01f7fbade8d6ffab263e781274cffca0dba9be9eec9 \
+    --hash=sha256:1dd9b0b119a350976a6d781e7278ec7aca0b201e1a9e2d23d9804afecb6ca681 \
+    --hash=sha256:1f1489f769582498610e015a8ef2d36f28f505ab3096d0e16b4858a9ec214f57 \
+    --hash=sha256:2517e24d7315eb51c10664cdb865195df38ab74456c677df67bb47f12d088a27 \
+    --hash=sha256:295d9ffe712caa9f8a3081de8d32fc60191b4b51c76f02f951fd8407253528f4 \
+    --hash=sha256:2a075bd7bd19c70cf67c8badfa36cf7c5d8de3c9ddb8420c51e10d9c50e94920 \
+    --hash=sha256:32cc0a5365239a6ea0c6ed461e8838d053b57e397443c0ca894dcc8e388d4374 \
+    --hash=sha256:332b4f0145c30b5f5ad9374881133e5aa64320428a57c2c2b61e9d891a51c2f3 \
+    --hash=sha256:377815a8616074cabbf3f53354e1d040c35815a134e01d7614b7692e4bf8acfa \
+    --hash=sha256:38f4a703656f493b0ad185211ccfca7f0386120f022066b018eb5296d8613e23 \
+    --hash=sha256:3ac2360e93cb41be81121755c6462cff3beaa9967188c866e5fce5cf13170859 \
+    --hash=sha256:3c4923e404d6bcd91b6779c009542e5647fef32e4a5d75e115e3bbac6f2335eb \
+    --hash=sha256:3cdcb35dc9d807259c981a85531048ede628eabcffb3239adf3d17463518992d \
+    --hash=sha256:41024ed50e44ab1a60d3fe0a9d15a4ccc9f5f2b1d814ff283c8d01134d5b81bc \
+    --hash=sha256:413b820229730d358efd838ecbab79902fe97094565fdc80ddb6b0a18c18a581 \
+    --hash=sha256:4432b835675f0ea7414aab3d37d119f7226d24869b7a829caeab49ebda407b0c \
+    --hash=sha256:4db576bb8c3ef9365f8b40fe0f671644de6736ae2c27a2c62d7d8a1b4329f099 \
+    --hash=sha256:4e7f886f47ab881692f278ae901039a234e4025a68e6dfab514263a0b1c4ae05 \
+    --hash=sha256:4e9750bc21b886308024f8a54ccb9a2cc38ac9fa813bf4348434e3d54f337ff9 \
+    --hash=sha256:5060731cc3ed12ca3a8b57acd4aeca5bbc2f49216dd0bec1650a1acd89486bcd \
+    --hash=sha256:50847dca5d197fcbd389c805aa1a1cf32f25d2e7273dc47ab181a517666b68cc \
+    --hash=sha256:5092eb5b1172947f57d6ea7d89b2f29650414e4293c47707eb499ec07a0ac796 \
+    --hash=sha256:5124d1ea754509b09e53738ec185584cc609aae4a3b510aaf4ed6aa047ef9303 \
+    --hash=sha256:51e8c4084897de9f05898c2c2a39af6318044ae969d46ff7a34ed3f96274adca \
+    --hash=sha256:530a3fd64c87cffa844d4b6b9768774763d9caa299e9b75d8eca6a4423b31314 \
+    --hash=sha256:56fa888f10d0f367155e76ce849fa1166fc9730d13bd2d65a2aa13b6f5424489 \
+    --hash=sha256:58f812017cd2985c21fbffb4864d59174d4903dd66fa23815e74bbc7a0e2dd57 \
+    --hash=sha256:59cd8683f575d96df5bb48f6add94afc055012c29e28124fcae2b63661b9efb1 \
+    --hash=sha256:5ae8e62c147495b01a0f4765c878e9bfdf843412446a247e28df59936e99e797 \
+    --hash=sha256:5b233ea3e165e43e35dba1d2b8ecc21cf070b45b65ae17dd2747d2713d942021 \
+    --hash=sha256:6176c1811d9d5a04fa391c490cc44f451e240697a16977f11c6f722efb9041db \
+    --hash=sha256:62f59da443c4f4849f73a51a193b1d9d258dcad0c41bc4d1b8fb2bcc04bfeb22 \
+    --hash=sha256:6783e069732715ad0c3ce96dbf21dbc2235ab0593f2baf6338101f70371f4028 \
+    --hash=sha256:6ab8ba9152203feec73758dad83af9a0bbe05001eb4639e547207c40cfb52083 \
+    --hash=sha256:70d593af6a6ca332d1df73d519fddb5148edb15cd90d5f0155e3746a6d4fcc65 \
+    --hash=sha256:72ec46b7eba5b395e0a7b63025490d3214c11013f4aacb4f5e8d6c3041829588 \
+    --hash=sha256:7a32f72973f0f950c1920475d5c5ea3d971b81b6f0ec53b8d0a956cc965f22e0 \
+    --hash=sha256:7a4aa69609f40fce3cbc3f87b2061f042eee32f94b8f11db707b66a26461591a \
+    --hash=sha256:7c60d3c9b06fb23bd9c6139281ccbdc384297579ae037f08ae90c69f6845c0b1 \
+    --hash=sha256:800ee55980c18545af444d93fdd60c56b580db5cc54867d8cbf8a1dc0829938c \
+    --hash=sha256:80aa065ffd378ff784822a6d7c3212f2d5f5e9c3589614b5c228b311fd3063ac \
+    --hash=sha256:86e0287879f75621ae85197b0877ed2f8b7aa57b511c7331dce2eb6f4de7d476 \
+    --hash=sha256:893ff3a711d1b515ba9da14ee090519bad4610ed1962fbe298a434e8c5f8db53 \
+    --hash=sha256:89fc958c702ee9a745e4700378f5d23fddbc46ff89e8fdbf5395c24d5c1452a3 \
+    --hash=sha256:8c63c91f95173f9c2a67c7c526b2cea976828a0e7fced9cdcead2802dc10f8a4 \
+    --hash=sha256:8df31fe574b8b3993cc61764f40941111b25c2d9fea13d3ce24a49907cd2d615 \
+    --hash=sha256:8f9baf6f0a6e7571c45c8863010b45e837c3ee1c2c77fcd6ef423be91b21fedb \
+    --hash=sha256:9027d773c4ff81487181a925945743413f6069634d0b122d0b37684ccf4f1e18 \
+    --hash=sha256:9190426b7aa26c5229501fa297b8d0653cfd3f5a36f7990c264e157cbf886b3b \
+    --hash=sha256:940dda65d5e764406b9fb92761cbf462e4e63f712ab60ed98f70552e496f3bf1 \
+    --hash=sha256:94eff26096eb5395136634622515b234ecb6c9979824c1f5004c6e3c3c85ccd2 \
+    --hash=sha256:9eed0f7edbb274413b6ee781cca50541c8c0facd3d6fd289779e494340a2b85c \
+    --hash=sha256:ad4ae4ffd1ee9cd11357b4c66b612da9888f4f4daf2f36995eda64bd45370cac \
+    --hash=sha256:b0f172dc8ffaccb8522d7c5d899de00133f2f1ca7b0a49b7da98e901de87bf2d \
+    --hash=sha256:b2af221f268f5af85e776a73d62b0845fc8baf8ef0abfae79d29c77d0e776aaf \
+    --hash=sha256:b7d335370ae48a780c6e6a6bbfa97342f563744c39c35562f3f367665f5c1de2 \
+    --hash=sha256:b83af57bdddef03c01a9138034c6ff03181a3028d9a1003b301eb1a55e161a3f \
+    --hash=sha256:bb5136fb5352d3f422df33f0c879a1b0c204004324150cc3b5e3c4f310c9049f \
+    --hash=sha256:bc4d8e252f532ab46a1de9349e2d27b91fce46736a9eedaa37beaca66f574ed4 \
+    --hash=sha256:bdd3e53429ff02aa319ba59dfe4ceeec345bf46cf180ec2cf6fd5b942e7975e9 \
+    --hash=sha256:be12f931839a3bdfe28b584db0e640a65a8bcbc24560ae3fdb025a449b3d754e \
+    --hash=sha256:be4a51a55833dc29ab5d7503e7bcb3b3af3402d266018137127450005cdfe737 \
+    --hash=sha256:beb7f344487cdcb9e1efe4b7a29681b74d34c08f0043a327a74da852a6749e7b \
+    --hash=sha256:bf4679a3d71012a7c2bf360e5cd878fbd5e4fcac0896b56393dec239d81529ed \
+    --hash=sha256:c0e1403fd7c26d77c1f03e096dc58a5c726503fa0db0456678b8668f76f521e3 \
+    --hash=sha256:c31c13da98624f957b0fb1b5bae5383b2333c2c3f6793d9825dd5ce79b525cb7 \
+    --hash=sha256:c438f6ca858697c9ab67eb28246c92508af972e114cac34e57a6d4ba17a3ac08 \
+    --hash=sha256:c8277104ded0a51e699c8c3aff63ce2c56d4ed5519a5f73e0fd7057f959a2b9e \
+    --hash=sha256:c95cab08d1965db3d84a121f1c7ce7479bdd4072c9b3dafd8fecce48a2e6b902 \
+    --hash=sha256:cc0b66c1eec9021353a4b4483afb12dfd50e3669ffbb9152d6842eb34c7e29fd \
+    --hash=sha256:cdee07c4d7f6d72008d3f73b9bf027f4e11550224c7c50d8df1ae4a37c1402a6 \
+    --hash=sha256:ce9bf03dad3b46408c08649c6fbd6ca28a9fce0eb32fdfffa6775a13103b5310 \
+    --hash=sha256:cff8e5383db4989311f99e814feeb90c4723eb4edca425b9d5d9c3fefcdd9537 \
+    --hash=sha256:d168fda2dbff7b9b5f38e693182d792a938c31db4dac3a80a4888de603c99554 \
+    --hash=sha256:d1ffeb80b5676463d7a7d56acbe8e37a20ce725570e09549fe738e02ca6b7e1e \
+    --hash=sha256:d36ca54cb4c6c4686f7cbb7b817f66f5911c12ddb519450bbe86707155028f87 \
+    --hash=sha256:d4193f3d9dc3f6f79aaed0e5637f45d98850ebf01f7ca20e69457f3e8946b66a \
+    --hash=sha256:d5cd5189fc2b6a538b75ae45433140c4823463918f7b1617c31e68b085c0022c \
+    --hash=sha256:d618fd27420381a4f6044faa71f46d8bfd911bd077c555f7138ed88729bfbe79 \
+    --hash=sha256:d76e2d8c75051d58177e762164d2e9ab92886534e3a12e795f103524f221dd8e \
+    --hash=sha256:daae526907e262de627d8f70058a0f64acc9e2641c164c99c8f594b34a799a16 \
+    --hash=sha256:db485b3847d182b908b483b2ed133c66d88d49cacf98fd278fadafe11b4478d1 \
+    --hash=sha256:dd952e03bfbb096cfe2dd35cd9e00f269969b67536cb4370994afc20ff2d0875 \
+    --hash=sha256:dda366d548e89a90d88a86c692377d18d8bd64b39c1fb2b92cb31370e2896bbd \
+    --hash=sha256:e315e5ec90d88e140f57696ff85b484ff68bb311e36f2c414aa4286293e6dee0 \
+    --hash=sha256:e4415a8db000bf49a6dd1c478bf70062eaacff0f462b92b0ba68791a905861f9 \
+    --hash=sha256:e7a116ae737f0000343218c4edf5bd45893bfeaff0993c0b215d7124c9f77646 \
+    --hash=sha256:e7c4c09a490dc4d4a7f8cbee56c606a320f9dc28cf92a7157a39d1ce7676a657 \
+    --hash=sha256:ebae99ed6764f2b5771c522477b311be313e8841d2e0376db2b10922daebbba4 \
+    --hash=sha256:ec4c85dc4b687c7f7f15f553ff26a98bfe8c58f5f7f0ac8905f0ba4c7be60232 \
+    --hash=sha256:ed3a984b31da7481b103f68776f7128a89ef26ed40f4dc41a2223cda7fb24819 \
+    --hash=sha256:f18c2d9782259a6dc132fdc7a63c168cbc74b35284b6d75c673958982a378384 \
+    --hash=sha256:f1f9f4121ec58628c96baa3de1a55a4e3a333c5102c8e94b64e23bf7b2083309 \
+    --hash=sha256:f42c23db5d1521218a3276bb08666dcb662896a0be7347cba864eca45ff64ede \
+    --hash=sha256:f443b4825c50a51ee68585522ab4a1d1257fac65896f282b4c6763337ac9f5d2 \
+    --hash=sha256:f6764a4ccab3078db14a632420930f6186058750df066b8ea2a7106df91d3203 \
+    --hash=sha256:f7c7553b13f69c1b29a5bde08ddc6d9d0c8bfb84f9ed01c30db25944aeb852a7 \
+    --hash=sha256:fa6248cd194edff41d7ea9425ced8ca3a6f838bfb295f6f1d6e6bb694a8518df \
+    --hash=sha256:fa8eb9ecdb7efb0b226acec134e0d709e87a909fa4971a54c0c4f6e88635484c \
+    --hash=sha256:fc20894c3d21194d8041a28b65622d5b86db786da6e3cfe73f0c762951a61167 \
+    --hash=sha256:fc4d3f1fb9ca0ae9f97b095963bc6326f1dbfd3779d6679a1e016b9baaa153d3 \
+    --hash=sha256:fd40bb9cd0891c4c3cb1ddf83f8bbfa15731a248fdc8162669405451e2724b09 \
+    --hash=sha256:ff710414307fefa903e0d9bdf300972f892c23477829f49504e59834f4195398
+    # via matplotlib
+lightgbm==4.6.0 \
+    --hash=sha256:2dafd98d4e02b844ceb0b61450a660681076b1ea6c7adb8c566dfd66832aafad \
+    --hash=sha256:37089ee95664b6550a7189d887dbf098e3eadab03537e411f52c63c121e3ba4b \
+    --hash=sha256:4d68712bbd2b57a0b14390cbf9376c1d5ed773fa2e71e099cac588703b590336 \
+    --hash=sha256:b7a393de8a334d5c8e490df91270f0763f83f959574d504c7ccb9eee4aef70ed \
+    --hash=sha256:cb19b5afea55b5b61cbb2131095f50538bd608a00655f23ad5d25ae3e3bf1c8d \
+    --hash=sha256:cb1c59720eb569389c0ba74d14f52351b573af489f230032a1c9f314f8bab7fe
+    # via -r requirements.in
+llvmlite==0.47.0 \
+    --hash=sha256:003bcf7fa579e14db59c1a1e113f93ab8a06b56a4be31c7f08264d1d4072d077 \
+    --hash=sha256:12a69d4bb05f402f30477e21eeabe81911e7c251cecb192bed82cd83c9db10d8 \
+    --hash=sha256:166b896a2262a2039d5fc52df5ee1659bd1ccd081183df7a2fba1b74702dd5ea \
+    --hash=sha256:2699a74321189e812d476a43d6d7f652f51811e7b5aad9d9bba842a1c7927acb \
+    --hash=sha256:306a265f408c259067257a732c8e159284334018b4083a9e35f67d19792b164f \
+    --hash=sha256:41270b0b1310717f717cf6f2a9c68d3c43bd7905c33f003825aebc361d0d1b17 \
+    --hash=sha256:5853bf26160857c0c2573415ff4efe01c4c651e59e2c55c2a088740acfee51cd \
+    --hash=sha256:62031ce968ec74e95092184d4b0e857e444f8fdff0b8f9213707699570c33ccc \
+    --hash=sha256:6842cf6f707ec4be3d985a385ad03f72b2d724439e118fcbe99b2929964f0453 \
+    --hash=sha256:694e3c2cdc472ed2bd8bd4555ca002eec4310961dd58ef791d508f57b5cc4c94 \
+    --hash=sha256:6c6951e2b29930227963e53ee152441f0e14be92e9d4231852102d986c761e40 \
+    --hash=sha256:74090f0dcfd6f24ebbef3f21f11e38111c4d7e6919b54c4416e1e357c3446b07 \
+    --hash=sha256:92ec8a169a20b473c1c54d4695e371bde36489fc1efa3688e11e99beba0abf9c \
+    --hash=sha256:9ea5cfb04a6ab5b18e46be72b41b015975ba5980c4ddb41f1975b83e19031063 \
+    --hash=sha256:a3c6a735d4e1041808434f9d440faa3d78d9b4af2ee64d05a66f351883b6ceec \
+    --hash=sha256:c2e9adf8698d813a9a5efb2d4370caf344dbc1e145019851fee6a6f319ba760e \
+    --hash=sha256:c37d6eb7aaabfa83ab9c2ff5b5cdb95a5e6830403937b2c588b7490724e05327 \
+    --hash=sha256:ca14f02e29134e837982497959a8e2193d6035235de1cb41a9cb2bd6da4eedbb \
+    --hash=sha256:d4a7b778a2e144fc64468fb9bf509ac1226c9813a00b4d7afea5d988c4e22fca \
+    --hash=sha256:ddbccff2aeaff8670368340a158abefc032fe9b3ccf7d9c496639263d00151aa \
+    --hash=sha256:de966c626c35c9dff5ae7bf12db25637738d0df83fc370cf793bc94d43d92d14 \
+    --hash=sha256:f3079f25bdc24cd9d27c4b2b5e68f5f60c4fdb7e8ad5ee2b9b006007558f9df7 \
+    --hash=sha256:f6725179b89f03b17dabe236ff3422cb8291b4c1bf40af152826dfd34e350ae8 \
+    --hash=sha256:f9d118bc1dd7623e0e65ca9ac485ec6dd543c3b77bc9928ddc45ebd34e1e30a7 \
+    --hash=sha256:fa1cbd800edd3b20bc141521f7fd45a6185a5b84109aa6855134e81397ffe72b
+    # via
+    #   numba
+    #   pynndescent
+    #   shap
+mako==1.3.12 \
+    --hash=sha256:8f61569480282dbf557145ce441e4ba888be453c30989f879f0d652e39f53ea9 \
+    --hash=sha256:9f778e93289bd410bb35daadeb4fc66d95a746f0b75777b942088b7fd7af550a
+    # via alembic
+markdown-it-py==4.0.0 \
+    --hash=sha256:87327c59b172c5011896038353a81343b6754500a08cd7a4973bb48c6d578147 \
+    --hash=sha256:cb0a2b4aa34f932c007117b194e945bd74e0ec24133ceb5bac59009cda1cb9f3
+    # via
+    #   jupytext
+    #   mdit-py-plugins
+markupsafe==3.0.3 \
+    --hash=sha256:0303439a41979d9e74d18ff5e2dd8c43ed6c6001fd40e5bf2e43f7bd9bbc523f \
+    --hash=sha256:068f375c472b3e7acbe2d5318dea141359e6900156b5b2ba06a30b169086b91a \
+    --hash=sha256:0bf2a864d67e76e5c9a34dc26ec616a66b9888e25e7b9460e1c76d3293bd9dbf \
+    --hash=sha256:0db14f5dafddbb6d9208827849fad01f1a2609380add406671a26386cdf15a19 \
+    --hash=sha256:0eb9ff8191e8498cca014656ae6b8d61f39da5f95b488805da4bb029cccbfbaf \
+    --hash=sha256:0f4b68347f8c5eab4a13419215bdfd7f8c9b19f2b25520968adfad23eb0ce60c \
+    --hash=sha256:1085e7fbddd3be5f89cc898938f42c0b3c711fdcb37d75221de2666af647c175 \
+    --hash=sha256:116bb52f642a37c115f517494ea5feb03889e04df47eeff5b130b1808ce7c219 \
+    --hash=sha256:12c63dfb4a98206f045aa9563db46507995f7ef6d83b2f68eda65c307c6829eb \
+    --hash=sha256:133a43e73a802c5562be9bbcd03d090aa5a1fe899db609c29e8c8d815c5f6de6 \
+    --hash=sha256:1353ef0c1b138e1907ae78e2f6c63ff67501122006b0f9abad68fda5f4ffc6ab \
+    --hash=sha256:15d939a21d546304880945ca1ecb8a039db6b4dc49b2c5a400387cdae6a62e26 \
+    --hash=sha256:177b5253b2834fe3678cb4a5f0059808258584c559193998be2601324fdeafb1 \
+    --hash=sha256:1872df69a4de6aead3491198eaf13810b565bdbeec3ae2dc8780f14458ec73ce \
+    --hash=sha256:1b4b79e8ebf6b55351f0d91fe80f893b4743f104bff22e90697db1590e47a218 \
+    --hash=sha256:1b52b4fb9df4eb9ae465f8d0c228a00624de2334f216f178a995ccdcf82c4634 \
+    --hash=sha256:1ba88449deb3de88bd40044603fafffb7bc2b055d626a330323a9ed736661695 \
+    --hash=sha256:1cc7ea17a6824959616c525620e387f6dd30fec8cb44f649e31712db02123dad \
+    --hash=sha256:218551f6df4868a8d527e3062d0fb968682fe92054e89978594c28e642c43a73 \
+    --hash=sha256:26a5784ded40c9e318cfc2bdb30fe164bdb8665ded9cd64d500a34fb42067b1c \
+    --hash=sha256:2713baf880df847f2bece4230d4d094280f4e67b1e813eec43b4c0e144a34ffe \
+    --hash=sha256:2a15a08b17dd94c53a1da0438822d70ebcd13f8c3a95abe3a9ef9f11a94830aa \
+    --hash=sha256:2f981d352f04553a7171b8e44369f2af4055f888dfb147d55e42d29e29e74559 \
+    --hash=sha256:32001d6a8fc98c8cb5c947787c5d08b0a50663d139f1305bac5885d98d9b40fa \
+    --hash=sha256:3524b778fe5cfb3452a09d31e7b5adefeea8c5be1d43c4f810ba09f2ceb29d37 \
+    --hash=sha256:3537e01efc9d4dccdf77221fb1cb3b8e1a38d5428920e0657ce299b20324d758 \
+    --hash=sha256:35add3b638a5d900e807944a078b51922212fb3dedb01633a8defc4b01a3c85f \
+    --hash=sha256:38664109c14ffc9e7437e86b4dceb442b0096dfe3541d7864d9cbe1da4cf36c8 \
+    --hash=sha256:3a7e8ae81ae39e62a41ec302f972ba6ae23a5c5396c8e60113e9066ef893da0d \
+    --hash=sha256:3b562dd9e9ea93f13d53989d23a7e775fdfd1066c33494ff43f5418bc8c58a5c \
+    --hash=sha256:457a69a9577064c05a97c41f4e65148652db078a3a509039e64d3467b9e7ef97 \
+    --hash=sha256:4bd4cd07944443f5a265608cc6aab442e4f74dff8088b0dfc8238647b8f6ae9a \
+    --hash=sha256:4e885a3d1efa2eadc93c894a21770e4bc67899e3543680313b09f139e149ab19 \
+    --hash=sha256:4faffd047e07c38848ce017e8725090413cd80cbc23d86e55c587bf979e579c9 \
+    --hash=sha256:509fa21c6deb7a7a273d629cf5ec029bc209d1a51178615ddf718f5918992ab9 \
+    --hash=sha256:5678211cb9333a6468fb8d8be0305520aa073f50d17f089b5b4b477ea6e67fdc \
+    --hash=sha256:591ae9f2a647529ca990bc681daebdd52c8791ff06c2bfa05b65163e28102ef2 \
+    --hash=sha256:5a7d5dc5140555cf21a6fefbdbf8723f06fcd2f63ef108f2854de715e4422cb4 \
+    --hash=sha256:69c0b73548bc525c8cb9a251cddf1931d1db4d2258e9599c28c07ef3580ef354 \
+    --hash=sha256:6b5420a1d9450023228968e7e6a9ce57f65d148ab56d2313fcd589eee96a7a50 \
+    --hash=sha256:722695808f4b6457b320fdc131280796bdceb04ab50fe1795cd540799ebe1698 \
+    --hash=sha256:729586769a26dbceff69f7a7dbbf59ab6572b99d94576a5592625d5b411576b9 \
+    --hash=sha256:77f0643abe7495da77fb436f50f8dab76dbc6e5fd25d39589a0f1fe6548bfa2b \
+    --hash=sha256:795e7751525cae078558e679d646ae45574b47ed6e7771863fcc079a6171a0fc \
+    --hash=sha256:7be7b61bb172e1ed687f1754f8e7484f1c8019780f6f6b0786e76bb01c2ae115 \
+    --hash=sha256:7c3fb7d25180895632e5d3148dbdc29ea38ccb7fd210aa27acbd1201a1902c6e \
+    --hash=sha256:7e68f88e5b8799aa49c85cd116c932a1ac15caaa3f5db09087854d218359e485 \
+    --hash=sha256:83891d0e9fb81a825d9a6d61e3f07550ca70a076484292a70fde82c4b807286f \
+    --hash=sha256:8485f406a96febb5140bfeca44a73e3ce5116b2501ac54fe953e488fb1d03b12 \
+    --hash=sha256:8709b08f4a89aa7586de0aadc8da56180242ee0ada3999749b183aa23df95025 \
+    --hash=sha256:8f71bc33915be5186016f675cd83a1e08523649b0e33efdb898db577ef5bb009 \
+    --hash=sha256:915c04ba3851909ce68ccc2b8e2cd691618c4dc4c4232fb7982bca3f41fd8c3d \
+    --hash=sha256:949b8d66bc381ee8b007cd945914c721d9aba8e27f71959d750a46f7c282b20b \
+    --hash=sha256:94c6f0bb423f739146aec64595853541634bde58b2135f27f61c1ffd1cd4d16a \
+    --hash=sha256:9a1abfdc021a164803f4d485104931fb8f8c1efd55bc6b748d2f5774e78b62c5 \
+    --hash=sha256:9b79b7a16f7fedff2495d684f2b59b0457c3b493778c9eed31111be64d58279f \
+    --hash=sha256:a320721ab5a1aba0a233739394eb907f8c8da5c98c9181d1161e77a0c8e36f2d \
+    --hash=sha256:a4afe79fb3de0b7097d81da19090f4df4f8d3a2b3adaa8764138aac2e44f3af1 \
+    --hash=sha256:ad2cf8aa28b8c020ab2fc8287b0f823d0a7d8630784c31e9ee5edea20f406287 \
+    --hash=sha256:b8512a91625c9b3da6f127803b166b629725e68af71f8184ae7e7d54686a56d6 \
+    --hash=sha256:bc51efed119bc9cfdf792cdeaa4d67e8f6fcccab66ed4bfdd6bde3e59bfcbb2f \
+    --hash=sha256:bdc919ead48f234740ad807933cdf545180bfbe9342c2bb451556db2ed958581 \
+    --hash=sha256:bdd37121970bfd8be76c5fb069c7751683bdf373db1ed6c010162b2a130248ed \
+    --hash=sha256:be8813b57049a7dc738189df53d69395eba14fb99345e0a5994914a3864c8a4b \
+    --hash=sha256:c0c0b3ade1c0b13b936d7970b1d37a57acde9199dc2aecc4c336773e1d86049c \
+    --hash=sha256:c47a551199eb8eb2121d4f0f15ae0f923d31350ab9280078d1e5f12b249e0026 \
+    --hash=sha256:c4ffb7ebf07cfe8931028e3e4c85f0357459a3f9f9490886198848f4fa002ec8 \
+    --hash=sha256:ccfcd093f13f0f0b7fdd0f198b90053bf7b2f02a3927a30e63f3ccc9df56b676 \
+    --hash=sha256:d2ee202e79d8ed691ceebae8e0486bd9a2cd4794cec4824e1c99b6f5009502f6 \
+    --hash=sha256:d53197da72cc091b024dd97249dfc7794d6a56530370992a5e1a08983ad9230e \
+    --hash=sha256:d6dd0be5b5b189d31db7cda48b91d7e0a9795f31430b7f271219ab30f1d3ac9d \
+    --hash=sha256:d88b440e37a16e651bda4c7c2b930eb586fd15ca7406cb39e211fcff3bf3017d \
+    --hash=sha256:de8a88e63464af587c950061a5e6a67d3632e36df62b986892331d4620a35c01 \
+    --hash=sha256:df2449253ef108a379b8b5d6b43f4b1a8e81a061d6537becd5582fba5f9196d7 \
+    --hash=sha256:e1c1493fb6e50ab01d20a22826e57520f1284df32f2d8601fdd90b6304601419 \
+    --hash=sha256:e1cf1972137e83c5d4c136c43ced9ac51d0e124706ee1c8aa8532c1287fa8795 \
+    --hash=sha256:e2103a929dfa2fcaf9bb4e7c091983a49c9ac3b19c9061b6d5427dd7d14d81a1 \
+    --hash=sha256:e56b7d45a839a697b5eb268c82a71bd8c7f6c94d6fd50c3d577fa39a9f1409f5 \
+    --hash=sha256:e8afc3f2ccfa24215f8cb28dcf43f0113ac3c37c2f0f0806d8c70e4228c5cf4d \
+    --hash=sha256:e8fc20152abba6b83724d7ff268c249fa196d8259ff481f3b1476383f8f24e42 \
+    --hash=sha256:eaa9599de571d72e2daf60164784109f19978b327a3910d3e9de8c97b5b70cfe \
+    --hash=sha256:ec15a59cf5af7be74194f7ab02d0f59a62bdcf1a537677ce67a2537c9b87fcda \
+    --hash=sha256:f190daf01f13c72eac4efd5c430a8de82489d9cff23c364c3ea822545032993e \
+    --hash=sha256:f34c41761022dd093b4b6896d4810782ffbabe30f2d443ff5f083e0cbbb8c737 \
+    --hash=sha256:f3e98bb3798ead92273dc0e5fd0f31ade220f59a266ffd8a4f6065e0a3ce0523 \
+    --hash=sha256:f42d0984e947b8adf7dd6dde396e720934d12c506ce84eea8476409563607591 \
+    --hash=sha256:f71a396b3bf33ecaa1626c255855702aca4d3d9fea5e051b41ac59a9c1c41edc \
+    --hash=sha256:f9e130248f4462aaa8e2552d547f36ddadbeaa573879158d721bbd33dfe4743a \
+    --hash=sha256:fed51ac40f757d41b7c48425901843666a6677e3e8eb0abcff09e4ba6e664f50
+    # via
+    #   jinja2
+    #   mako
+matplotlib==3.10.9 \
+    --hash=sha256:09218df8a93712bd6ea133e83a153c755448cf7868316c531cffcc43f69d1cc9 \
+    --hash=sha256:10cc5ce06d10231c36f40e875f3c7e8050362a4ee8f0ee5d29a6b3277d57bb42 \
+    --hash=sha256:172db52c9e683f5d12eaf57f0f54834190e12581fe1cc2a19595a8f5acb4e77d \
+    --hash=sha256:1872fb212a05b729e649754a72d5da61d03e0554d76e80303b6f83d1d2c0552b \
+    --hash=sha256:1aa972116abb4c9d201bf245620b433726cb6856f3bef6a78f776a00f5c92d37 \
+    --hash=sha256:1e7698ac9868428e84d2c967424803b2472ff7167d9d6590d4204ed775343c3b \
+    --hash=sha256:2dc9477819ffd78ad12a20df1d9d6a6bd4fec6aaa9072681465fddca052f1456 \
+    --hash=sha256:3225f4e1edcb8c86c884ddf79ebe20ecd0a67d30188f279897554ccd8fded4dc \
+    --hash=sha256:336b9acc64d309063126edcdaca00db9373af3c476bb94388fe9c5a53ad13e6f \
+    --hash=sha256:345f6f68ecc8da0ca56fad2ea08fde1a115eda530079eca185d50a7bc3e146c6 \
+    --hash=sha256:34cf8167e023ad956c15f36302911d5406bd99a9862c1a8499ea6f7c0e015dc2 \
+    --hash=sha256:3fc0364dfbe1d07f6d15c5ebd0c5bf89e126916e5a8667dd4a7a6e84c36653d4 \
+    --hash=sha256:41cb28c2bd769aa3e98322c6ab09854cbcc52ab69d2759d681bba3e327b2b320 \
+    --hash=sha256:42fb814efabe95c06c1994d8ab5a8385f43a249e23badd3ba931d4308e5bca20 \
+    --hash=sha256:4e42042d54db34fda4e95a7bd3e5789c2a995d2dad3eb8850232ee534092fbbf \
+    --hash=sha256:4edcfbd8565339aa62f1cd4012f7180926fdbe71850f7b0d3c379c175cd6b66c \
+    --hash=sha256:51bf0ddbdc598e060d46c16b5590708f81a1624cefbaaf62f6a81bf9285b8c80 \
+    --hash=sha256:56fc0bd271b00025c6edfdc7c2dcd247372c8e1544971d62e1dc7c17367e8bf9 \
+    --hash=sha256:59476c6d29d612b8e9bb6ce8c5b631be6ba8f9e3a2421f22a02b192c7dd28716 \
+    --hash=sha256:6640f75af2c6148293caa0a2b39dd806a492dd66c8a8b04035813e33d0fd2585 \
+    --hash=sha256:68cfdcede415f7c8f5577b03303dd94526cdb6d11036cecdc205e08733b2d2bb \
+    --hash=sha256:6b63d9c7c769b88ab81e10dc86e4e0607cf56817b9f9e6cf24b2a5f1693b8e38 \
+    --hash=sha256:6be157fe17fc37cb95ac1d7374cf717ce9259616edec911a78d9d26dae8522d4 \
+    --hash=sha256:6c63ebcd8b4b169eb2f5c200552ae6b8be8999a005b6b507ed76fb8d7d674fe2 \
+    --hash=sha256:77210dce9cb8153dffc967efaae990543392563d5a376d4dd8539bebcb0ed217 \
+    --hash=sha256:7a8d66a55def891c33147ba3ba9bfcabf0b526a43764c818acbb4525e5ed0838 \
+    --hash=sha256:82368699727bfb7b0182e1aa13082e3c08e092fa1a25d3e1fd92405bff96f6d4 \
+    --hash=sha256:82834c3c292d24d3a8aae77cd2d20019de69d692a34a970e4fdb8d33e2ea3dda \
+    --hash=sha256:8e436d155fa8a3399dc62683f8f5d0e2e50d25d0144a73edd73f82eec8f4abfb \
+    --hash=sha256:8f3bcac1ca5ed000a6f4337d47ba67dfddf37ed6a46c15fd7f014997f7bf865f \
+    --hash=sha256:97e35e8d39ccc85859095e01a53847432ba9a53ddf7986f7a54a11b73d0e143f \
+    --hash=sha256:985f2238880e2e69093f588f5fe2e46771747febf0649f3cf7f7b7480875317f \
+    --hash=sha256:a49f1eadc84ca85fd72fa4e89e70e61bf86452df6f971af04b12c60761a0772c \
+    --hash=sha256:a5a6104ed666402ba5106d7f36e0e0cdca4e8d7fa4d39708ca88019e2835a2eb \
+    --hash=sha256:aba1615dabe83188e19d4f75a253c6a08423e04c1425e64039f800050a69de6b \
+    --hash=sha256:ae20801130378b82d647ff5047c07316295b68dc054ca6b3c13519d0ea624285 \
+    --hash=sha256:ae2f11957b27ce53497dd4d7b235c4d4f1faf383dfb39d0c5beb833bff883294 \
+    --hash=sha256:b049278ddce116aaa1c1377ebf58adea909132dfce0281cf7e3a1ea9fc2e2c65 \
+    --hash=sha256:b1b745c489cd1a77a0dc1120a05dc87af9798faebc913601feb8c73d89bf2d1e \
+    --hash=sha256:b2b9516251cb89ff618d757daec0e2ed1bf21248013844a853d87ef85ab3081d \
+    --hash=sha256:b580440f1ff81a0e34122051a3dfabb7e4b7f9e380629929bde0eff9af72165f \
+    --hash=sha256:ba7b3b8ef09eab7df0e86e9ae086faa433efbfbdb46afcb3aa16aabf779469a8 \
+    --hash=sha256:c27df8b3848f32a83d1767566595e43cfaa4460380974da06f4279a7ec143c39 \
+    --hash=sha256:d091f9d758b34aaaaa6331d13574bf01891d903b3dec59bfff458ef7551de5d6 \
+    --hash=sha256:d730e984eddf56974c3e72b6129c7ca462ac38dc624338f4b0b23eb23ecba00f \
+    --hash=sha256:d75d11c949914165976c621b2324f9ef162af7ebf4b057ddf95dd1dba7e5edcf \
+    --hash=sha256:d843374407c4017a6403b59c6c81606773d136f3259d5b6da3131bc814542cc2 \
+    --hash=sha256:da4e09638420548f31c354032a6250e473c68e5a4e96899b4844cf39ddea23fe \
+    --hash=sha256:de2445a0c6690d21b7eb6ce071cebad6d40a2e9bdf10d039074a96ba19797b99 \
+    --hash=sha256:dfca0129678bd56379db26c52b5d77ed7de314c047492fbdc763aa7501710cfb \
+    --hash=sha256:e9fae004b941b23ff2edcf1567a857ed77bafc8086ffa258190462328434faf8 \
+    --hash=sha256:f0c3c28d9fbcc1fe7a03be236d73430cf6409c41fb2383a7ac52fe932b072cb1 \
+    --hash=sha256:f4399f64b3e94cd500195490972ae1ee81170df1636fa15364d157d5bdd7b921 \
+    --hash=sha256:f76e640a5268850bfda54b5131b1b1941cc685e42c5fa98ed9f2d64038308cba \
+    --hash=sha256:fd66508e8c6877d98e586654b608a0456db8d7e8a546eb1e2600efd957302358
+    # via prophet
+mdit-py-plugins==0.5.0 \
+    --hash=sha256:07a08422fc1936a5d26d146759e9155ea466e842f5ab2f7d2266dd084c8dab1f \
+    --hash=sha256:f4918cb50119f50446560513a8e311d574ff6aaed72606ddae6d35716fe809c6
+    # via jupytext
+mdurl==0.1.2 \
+    --hash=sha256:84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8 \
+    --hash=sha256:bb413d29f5eea38f31dd4754dd7377d4465116fb207585f97bf925588687c1ba
+    # via markdown-it-py
+mistune==2.0.5 \
+    --hash=sha256:0246113cb2492db875c6be56974a7c893333bf26cd92891c85f63151cee09d34 \
+    --hash=sha256:bad7f5d431886fcbaf5f758118ecff70d31f75231b34024a1341120340a65ce8
+    # via -r requirements.in
+narwhals==2.20.0 \
+    --hash=sha256:16e750ea5507d4ba6e8d03455b5f93a535e0405976561baea235bca5dc9f475d \
+    --hash=sha256:c10994975fa7dc5a68c2cffcddbd5908fc8ebb2d463c5bab085309c0ee1f551e
+    # via plotly
+nbclient==0.10.4 \
+    --hash=sha256:1e54091b16e6da39e297b0ece3e10f6f29f4ac4e8ee515d29f8a7099bd6553c9 \
+    --hash=sha256:9162df5a7373d70d606527300a95a975a47c137776cd942e52d9c7e29ff83440
+    # via papermill
+nbformat==5.10.4 \
+    --hash=sha256:322168b14f937a5d11362988ecac2a4952d3d8e3a2cbeb2319584631226d5b3a \
+    --hash=sha256:3b48d6c8fbca4b299bf3982ea7db1af21580e4fec269ad087b9e81588891200b
+    # via
+    #   jupytext
+    #   nbclient
+    #   nbstripout
+    #   papermill
+nbstripout==0.9.1 \
+    --hash=sha256:313bbb4217c8e38998567e5d790b6bd6c3a17a8c39073b205b84dadfc5d756dc \
+    --hash=sha256:ca027ee45742ee77e4f8e9080254f9a707f1161ba11367b82fdf4a29892c759e
+    # via -r requirements.in
+nodeenv==1.10.0 \
+    --hash=sha256:5bb13e3eed2923615535339b3c620e76779af4cb4c6a90deccc9e36b274d3827 \
+    --hash=sha256:996c191ad80897d076bdfba80a41994c2b47c68e224c542b48feba42ba00f8bb
+    # via pre-commit
+numba==0.65.1 \
+    --hash=sha256:1735c15c1134a5108b4d6a5c77fc0947924ea066a738dc09a52008c13df9cad3 \
+    --hash=sha256:19357146c32fe9ed25059ab915e8465fb13951cf6b0aace3826b76886373ab23 \
+    --hash=sha256:20609346e3bd75204950dcbbfe383a8d7dbf4902f442aedbf00f97fef4aa8f38 \
+    --hash=sha256:2a20fcdabdefbdacf88d85caf70c3b18c4bcb7ebb8f82e6a19486383dd26ab63 \
+    --hash=sha256:33f5eb68eb1c843511615d14663ce60258525d6a4c65ab040e2c2b0c4cf17450 \
+    --hash=sha256:3a07635e0be926b9bdbffb09137c230fb13f6ec0e564914ba937cee12ce3eb35 \
+    --hash=sha256:52bc6f3ceb8fcaff9b2ae26b4c6b1e9fee39db8d355534c0fe4f39a901246b84 \
+    --hash=sha256:548dd4b3a4508d5062768d1514b2cd7b015f9a25ec7af651c50dee243965e652 \
+    --hash=sha256:594a8680b3fadac99e97e489b1fd89007177e5336713745c3b769528c635a464 \
+    --hash=sha256:5971c632be2a2351500431f46213821dba8d02b18a9f7d02fd36bd2743e41a6a \
+    --hash=sha256:5f098109f361681e57295f7e84d8ab2426902539a141811de0703ace52826981 \
+    --hash=sha256:7020d74b19cdb8cff16506542fdd510756e28c5e7f3bd0b7f574f0f42272fcd9 \
+    --hash=sha256:71e73029bf53a62cc6afcf96be4bd942290d8b4c55f0a454fb536158115790f7 \
+    --hash=sha256:78abc28feff2c2ff8307fff3975b6438352759c9acb797ecd6b1fb6e7e39e31d \
+    --hash=sha256:7ed425a43b0a5f9772f2f4e2dd0bbd12eabecae1af0b24efcfd4e053f012aac6 \
+    --hash=sha256:85be74c0d036842699a30058f82fb88fc5ffdc59f7615cab5792ea92914c9b62 \
+    --hash=sha256:90ca10b3463bae0bd70589726fe3c77d01d6b5fc86bee54bcdf9fb6b47c28977 \
+    --hash=sha256:973fd8173f2312815e6b7aaae887c4ce8a817eeff46a4f8840b828305b75bc95 \
+    --hash=sha256:9d993ed0a257aa4116e6f553f114004bcfdee540c7276ab8ea48f650d514c452 \
+    --hash=sha256:ac3f1e77c352dd0ea9712732c2d8f9ca507717435eec5b5013bf138ac33c4a08 \
+    --hash=sha256:c09f49117ef255e1f1c6dad0c7a1ed39868243862a73be5706793241a3755f1b \
+    --hash=sha256:c63aa0c4193694026452da55d0ef9d85156c1a7a333454c103bb30dec81b7bf8 \
+    --hash=sha256:df40a5028a975b9ea66f6a2a3f7abbdbd541a863070e34ed367aff21141248e4 \
+    --hash=sha256:ee7676cb389555805f9b9a1840cbcd1ea6c8bd5376ab6918e3a29c5ea1dbda20 \
+    --hash=sha256:f80ed83774b5173abd6581cd8d2165d1d38e13d2e5c8155c0c0b421784745420
+    # via
+    #   pynndescent
+    #   shap
+    #   umap-learn
+numpy==2.3.5 \
+    --hash=sha256:00dc4e846108a382c5869e77c6ed514394bdeb3403461d25a829711041217d5b \
+    --hash=sha256:0472f11f6ec23a74a906a00b48a4dcf3849209696dff7c189714511268d103ae \
+    --hash=sha256:04822c00b5fd0323c8166d66c701dc31b7fbd252c100acd708c48f763968d6a3 \
+    --hash=sha256:052e8c42e0c49d2575621c158934920524f6c5da05a1d3b9bab5d8e259e045f0 \
+    --hash=sha256:09a1bea522b25109bf8e6f3027bd810f7c1085c64a0c7ce050c1676ad0ba010b \
+    --hash=sha256:0cd00b7b36e35398fa2d16af7b907b65304ef8bb4817a550e06e5012929830fa \
+    --hash=sha256:0d8163f43acde9a73c2a33605353a4f1bc4798745a8b1d73183b28e5b435ae28 \
+    --hash=sha256:1062fde1dcf469571705945b0f221b73928f34a20c904ffb45db101907c3454e \
+    --hash=sha256:11e06aa0af8c0f05104d56450d6093ee639e15f24ecf62d417329d06e522e017 \
+    --hash=sha256:17531366a2e3a9e30762c000f2c43a9aaa05728712e25c11ce1dbe700c53ad41 \
+    --hash=sha256:1978155dd49972084bd6ef388d66ab70f0c323ddee6f693d539376498720fb7e \
+    --hash=sha256:1ed1ec893cff7040a02c8aa1c8611b94d395590d553f6b53629a4461dc7f7b63 \
+    --hash=sha256:2dcd0808a421a482a080f89859a18beb0b3d1e905b81e617a188bd80422d62e9 \
+    --hash=sha256:2e2eb32ddb9ccb817d620ac1d8dae7c3f641c1e5f55f531a33e8ab97960a75b8 \
+    --hash=sha256:2feae0d2c91d46e59fcd62784a3a83b3fb677fead592ce51b5a6fbb4f95965ff \
+    --hash=sha256:3095bdb8dd297e5920b010e96134ed91d852d81d490e787beca7e35ae1d89cf7 \
+    --hash=sha256:30bc11310e8153ca664b14c5f1b73e94bd0503681fcf136a163de856f3a50139 \
+    --hash=sha256:3101e5177d114a593d79dd79658650fe28b5a0d8abeb8ce6f437c0e6df5be1a4 \
+    --hash=sha256:396084a36abdb603546b119d96528c2f6263921c50df3c8fd7cb28873a237748 \
+    --hash=sha256:3997b5b3c9a771e157f9aae01dd579ee35ad7109be18db0e85dbdbe1de06e952 \
+    --hash=sha256:414802f3b97f3c1eef41e530aaba3b3c1620649871d8cb38c6eaff034c2e16bd \
+    --hash=sha256:51c1e14eb1e154ebd80e860722f9e6ed6ec89714ad2db2d3aa33c31d7c12179b \
+    --hash=sha256:51c55fe3451421f3a6ef9a9c1439e82101c57a2c9eab9feb196a62b1a10b58ce \
+    --hash=sha256:5ee6609ac3604fa7780e30a03e5e241a7956f8e2fcfe547d51e3afa5247ac47f \
+    --hash=sha256:612a95a17655e213502f60cfb9bf9408efdc9eb1d5f50535cc6eb365d11b42b5 \
+    --hash=sha256:6203fdf9f3dc5bdaed7319ad8698e685c7a3be10819f41d32a0723e611733b42 \
+    --hash=sha256:63c0e9e7eea69588479ebf4a8a270d5ac22763cc5854e9a7eae952a3908103f7 \
+    --hash=sha256:66f85ce62c70b843bab1fb14a05d5737741e74e28c7b8b5a064de10142fad248 \
+    --hash=sha256:6cf9b429b21df6b99f4dee7a1218b8b7ffbbe7df8764dc0bd60ce8a0708fed1e \
+    --hash=sha256:70b37199913c1bd300ff6e2693316c6f869c7ee16378faf10e4f5e3275b299c3 \
+    --hash=sha256:727fd05b57df37dc0bcf1a27767a3d9a78cbbc92822445f32cc3436ba797337b \
+    --hash=sha256:74ae7b798248fe62021dbf3c914245ad45d1a6b0cb4a29ecb4b31d0bfbc4cc3e \
+    --hash=sha256:784db1dcdab56bf0517743e746dfb0f885fc68d948aba86eeec2cba234bdf1c0 \
+    --hash=sha256:86945f2ee6d10cdfd67bcb4069c1662dd711f7e2a4343db5cecec06b87cf31aa \
+    --hash=sha256:86d835afea1eaa143012a2d7a3f45a3adce2d7adc8b4961f0b362214d800846a \
+    --hash=sha256:872a5cf366aec6bb1147336480fef14c9164b154aeb6542327de4970282cd2f5 \
+    --hash=sha256:8b973c57ff8e184109db042c842423ff4f60446239bd585a5131cc47f06f789d \
+    --hash=sha256:8cba086a43d54ca804ce711b2a940b16e452807acebe7852ff327f1ecd49b0d4 \
+    --hash=sha256:8f7f0e05112916223d3f438f293abf0727e1181b5983f413dfa2fefc4098245c \
+    --hash=sha256:900218e456384ea676e24ea6a0417f030a3b07306d29d7ad843957b40a9d8d52 \
+    --hash=sha256:93eebbcf1aafdf7e2ddd44c2923e2672e1010bddc014138b229e49725b4d6be5 \
+    --hash=sha256:9c75442b2209b8470d6d5d8b1c25714270686f14c749028d2199c54e29f20b4d \
+    --hash=sha256:9ee2197ef8c4f0dfe405d835f3b6a14f5fee7782b5de51ba06fb65fc9b36e9f1 \
+    --hash=sha256:a414504bef8945eae5f2d7cb7be2d4af77c5d1cb5e20b296c2c25b61dff2900c \
+    --hash=sha256:a4b9159734b326535f4dd01d947f919c6eefd2d9827466a696c44ced82dfbc18 \
+    --hash=sha256:a80afd79f45f3c4a7d341f13acbe058d1ca8ac017c165d3fa0d3de6bc1a079d7 \
+    --hash=sha256:aa5bc7c5d59d831d9773d1170acac7893ce3a5e130540605770ade83280e7188 \
+    --hash=sha256:acfd89508504a19ed06ef963ad544ec6664518c863436306153e13e94605c218 \
+    --hash=sha256:aeffcab3d4b43712bb7a60b65f6044d444e75e563ff6180af8f98dd4b905dfd2 \
+    --hash=sha256:afaffc4393205524af9dfa400fa250143a6c3bc646c08c9f5e25a9f4b4d6a903 \
+    --hash=sha256:b0c7088a73aef3d687c4deef8452a3ac7c1be4e29ed8bf3b366c8111128ac60c \
+    --hash=sha256:b46b4ec24f7293f23adcd2d146960559aaf8020213de8ad1909dba6c013bf89c \
+    --hash=sha256:b501b5fa195cc9e24fe102f21ec0a44dffc231d2af79950b451e0d99cea02234 \
+    --hash=sha256:bf06bc2af43fa8d32d30fae16ad965663e966b1a3202ed407b84c989c3221e82 \
+    --hash=sha256:c804e3a5aba5460c73955c955bdbd5c08c354954e9270a2c1565f62e866bdc39 \
+    --hash=sha256:c8a9958e88b65c3b27e22ca2a076311636850b612d6bbfb76e8d156aacde2aaf \
+    --hash=sha256:cc0a57f895b96ec78969c34f682c602bf8da1a0270b09bc65673df2e7638ec20 \
+    --hash=sha256:cc8920d2ec5fa99875b670bb86ddeb21e295cb07aa331810d9e486e0b969d946 \
+    --hash=sha256:ccc933afd4d20aad3c00bcef049cb40049f7f196e0397f1109dba6fed63267b0 \
+    --hash=sha256:ce581db493ea1a96c0556360ede6607496e8bf9b3a8efa66e06477267bc831e9 \
+    --hash=sha256:d0f23b44f57077c1ede8c5f26b30f706498b4862d3ff0a7298b8411dd2f043ff \
+    --hash=sha256:d21644de1b609825ede2f48be98dfde4656aefc713654eeee280e37cadc4e0ad \
+    --hash=sha256:d6889ec4ec662a1a37eb4b4fb26b6100841804dac55bd9df579e326cdc146227 \
+    --hash=sha256:de5672f4a7b200c15a4127042170a694d4df43c992948f5e1af57f0174beed10 \
+    --hash=sha256:e6a0bc88393d65807d751a614207b7129a310ca4fe76a74e5c7da5fa5671417e \
+    --hash=sha256:ed89927b86296067b4f81f108a2271d8926467a8868e554eaf370fc27fa3ccaf \
+    --hash=sha256:ee3888d9ff7c14604052b2ca5535a30216aa0a58e948cdd3eeb8d3415f638769 \
+    --hash=sha256:f0963b55cdd70fad460fa4c1341f12f976bb26cb66021a5580329bd498988310 \
+    --hash=sha256:f16417ec91f12f814b10bafe79ef77e70113a2f5f7018640e7425ff979253425 \
+    --hash=sha256:f28620fe26bee16243be2b7b874da327312240a7cdc38b769a697578d2100013 \
+    --hash=sha256:f4255143f5160d0de972d28c8f9665d882b5f61309d8362fdd3e103cf7bf010c \
+    --hash=sha256:ffac52f28a7849ad7576293c0cb7b9f08304e8f7d738a8cb8a90ec4c55a998eb \
+    --hash=sha256:ffe22d2b05504f786c867c8395de703937f934272eb67586817b46188b4ded6d \
+    --hash=sha256:fffe29a1ef00883599d1dc2c51aa2e5d80afe49523c261a74933df395c15c520
+    # via
+    #   -r requirements.in
+    #   cmdstanpy
+    #   contourpy
+    #   lightgbm
+    #   matplotlib
+    #   numba
+    #   onnxruntime
+    #   optuna
+    #   pandas
+    #   patsy
+    #   pmdarima
+    #   prophet
+    #   scikit-learn
+    #   scipy
+    #   shap
+    #   stanio
+    #   statsmodels
+    #   umap-learn
+    #   xgboost
+nvidia-nccl-cu12==2.30.4 \
+    --hash=sha256:040974b261edec4b8b793e59e92ab7176fe4ab4bc61b800f9f3bfaeec2d436f3 \
+    --hash=sha256:606fa9aa9215c00367d060188eb1a5bbd28396aff5e11b9200d99d1a6ab79a71
+    # via xgboost
+onnxruntime==1.25.1 \
+    --hash=sha256:03e800b3a4b48d9f3a2d23aacc4fa95486a3b406b14e51d1a9b8b6981d9adf9c \
+    --hash=sha256:06280b06604660595037f783c6d24bc70cbe5c6093975f194cd1482e77d450de \
+    --hash=sha256:08717d6eee2820807ba60b1b17032af207bd7aaca5b6c4abaee71f83feae877b \
+    --hash=sha256:2affc9d2fd9ab013b9c9637464e649a0cca870d57ae18bfef74180eee65c3369 \
+    --hash=sha256:311d29b943e46a55ca72ca1ea48d7815c993122bfc359f68215fddeb9583fff4 \
+    --hash=sha256:3387d75d1a815b4b2495b4e47a05ef1b3bcb64a817ddc68587e0bfcb9702bcf6 \
+    --hash=sha256:395eb662c437fa2407f44266e4778b75bff261b17c2a6fef042421f9069f871d \
+    --hash=sha256:451b9494056f7f96b1be76a32745ccc4582bd61b2a0e1bc52de3708446151d5d \
+    --hash=sha256:5cf58ec7601120bb4370f0b868f794d3e3626db7b1b1dba366c27874b224e9de \
+    --hash=sha256:66e52f7a30d1f780a34aa84d68a0a04d382d9f5b141884ecbf45b7566b9fbde9 \
+    --hash=sha256:79162f873cdfa38cfc8d53d59a8dc7a71a14074df3d565b2f8ce24289545ddc0 \
+    --hash=sha256:7e608f8950076da02c0aeceec2dd790d201eeb31dd73acb04ec989b2bf6199dc \
+    --hash=sha256:7e79fd5ce7db10ebcc24e020e2ed0159476e69e2326b9b7828e5aadcf6184212 \
+    --hash=sha256:828e1b12710fbedb6dfab5e7bae6f11563617cddf3c2e7e8d84c64de566a4a3a \
+    --hash=sha256:84f8963d70e00167bae273ab7e80e9795bfc5eb94f6b23236a99c5c11af00844 \
+    --hash=sha256:905409e9eb2ef87f8226e073f56e71faf731c3e480ebd34952cf953730e4a4ff \
+    --hash=sha256:98016a038b31160db23208706139fa3b99cd60bc1c5ffdade77aafd6a37a92ad \
+    --hash=sha256:9ae85395f41b291ae3e61780ec5092640181d369ef6c268aa8141c478b509e69 \
+    --hash=sha256:a5f41779f044d1ff75593df5c10a4d311bc82563687796d5218e2685b8f9da25 \
+    --hash=sha256:b6c7aa5cae606d5c90a392679fac074b60f80025a2e83e1e90fdf882bd2a97f0 \
+    --hash=sha256:d4097b75b77486bb45835a8ed25b9a67976040ec6c258aeabae6aadfbdd1201c \
+    --hash=sha256:e9d9b3b1694196bc3c5bc66f760a237a5e27d7688aaa2e2c9c0f66abd0486699 \
+    --hash=sha256:fa7d4daa78a18b8f3b410e31e82dab8580363c85cac644179a853f2748618e89 \
+    --hash=sha256:fd83ef5c10cfc051a1cb465db692d57b996a1bc75a2a97b161398e29cdbc47ff
+    # via -r requirements.in
+optuna==4.8.0 \
+    --hash=sha256:6f7043e9f8ecb5e607af86a7eb00fb5ec2be26c3b08c201209a73d36aff37a38 \
+    --hash=sha256:c57a7682679c36bfc9bca0da430698179e513874074b71bebedb0334964ab930
+    # via -r requirements.in
+packaging==26.2 \
+    --hash=sha256:5fc45236b9446107ff2415ce77c807cee2862cb6fac22b8a73826d0693b0980e \
+    --hash=sha256:ff452ff5a3e828ce110190feff1178bb1f2ea2281fa2075aadb987c2fb221661
+    # via
+    #   jupytext
+    #   kaggle
+    #   matplotlib
+    #   onnxruntime
+    #   optuna
+    #   plotly
+    #   pmdarima
+    #   pytest
+    #   shap
+    #   statsmodels
+pandas==3.0.2 \
+    --hash=sha256:01f31a546acd5574ef77fe199bc90b55527c225c20ccda6601cf6b0fd5ed597c \
+    --hash=sha256:0555c5882688a39317179ab4a0ed41d3ebc8812ab14c69364bbee8fb7a3f6288 \
+    --hash=sha256:07a10f5c36512eead51bc578eb3354ad17578b22c013d89a796ab5eee90cd991 \
+    --hash=sha256:08504503f7101300107ecdc8df73658e4347586db5cfdadabc1592e9d7e7a0fd \
+    --hash=sha256:0f48afd9bb13300ffb5a3316973324c787054ba6665cda0da3fbd67f451995db \
+    --hash=sha256:140f0cffb1fa2524e874dde5b477d9defe10780d8e9e220d259b2c0874c89d9d \
+    --hash=sha256:232a70ebb568c0c4d2db4584f338c1577d81e3af63292208d615907b698a0f18 \
+    --hash=sha256:32cc41f310ebd4a296d93515fcac312216adfedb1894e879303987b8f1e2b97d \
+    --hash=sha256:339dda302bd8369dedeae979cb750e484d549b563c3f54f3922cb8ff4978c5eb \
+    --hash=sha256:4544c7a54920de8eeacaa1466a6b7268ecfbc9bc64ab4dbb89c6bbe94d5e0660 \
+    --hash=sha256:4d888a5c678a419a5bb41a2a93818e8ed9fd3172246555c0b37b7cc27027effd \
+    --hash=sha256:5371b72c2d4d415d08765f32d689217a43227484e81b2305b52076e328f6f482 \
+    --hash=sha256:57a07209bebcbcf768d2d13c9b78b852f9a15978dac41b9e6421a81ad4cdd276 \
+    --hash=sha256:5880314e69e763d4c8b27937090de570f1fb8d027059a7ada3f7f8e98bdcb677 \
+    --hash=sha256:5d3cfe227c725b1f3dff4278b43d8c784656a42a9325b63af6b1492a8232209e \
+    --hash=sha256:5fdbfa05931071aba28b408e59226186b01eb5e92bea2ab78b65863ca3228d84 \
+    --hash=sha256:60a80bb4feacbef5e1447a3f82c33209c8b7e07f28d805cfd1fb951e5cb443aa \
+    --hash=sha256:61c2fd96d72b983a9891b2598f286befd4ad262161a609c92dc1652544b46b76 \
+    --hash=sha256:63d141b56ef686f7f0d714cfb8de4e320475b86bf4b620aa0b7da89af8cbdbbb \
+    --hash=sha256:6c4d8458b97a35717b62469a4ea0e85abd5ed8687277f5ccfc67f8a5126f8c53 \
+    --hash=sha256:710246ba0616e86891b58ab95f2495143bb2bc83ab6b06747c74216f583a6ac9 \
+    --hash=sha256:734be7551687c00fbd760dc0522ed974f82ad230d4a10f54bf51b80d44a08702 \
+    --hash=sha256:7cadd7e9a44ec13b621aec60f9150e744cfc7a3dd32924a7e2f45edff31823b0 \
+    --hash=sha256:81526c4afd31971f8b62671442a4b2b51e0aa9acc3819c9f0f12a28b6fcf85f1 \
+    --hash=sha256:970762605cff1ca0d3f71ed4f3a769ea8f85fc8e6348f6e110b8fea7e6eb5a14 \
+    --hash=sha256:a3096110bf9eac0070b7208465f2740e2d8a670d5cb6530b5bb884eca495fd39 \
+    --hash=sha256:a4785e1d6547d8427c5208b748ae2efb64659a21bd82bf440d4262d02bfa02a4 \
+    --hash=sha256:a727a73cbdba2f7458dc82449e2315899d5140b449015d822f515749a46cbbe0 \
+    --hash=sha256:ae37e833ff4fed0ba352f6bdd8b73ba3ab3256a85e54edfd1ab51ae40cca0af8 \
+    --hash=sha256:aff4e6f4d722e0652707d7bcb190c445fe58428500c6d16005b02401764b1b3d \
+    --hash=sha256:b35d14bb5d8285d9494fe93815a9e9307c0876e10f1e8e89ac5b88f728ec8dcf \
+    --hash=sha256:b444dc64c079e84df91baa8bf613d58405645461cabca929d9178f2cd392398d \
+    --hash=sha256:b5329e26898896f06035241a626d7c335daa479b9bbc82be7c2742d048e41172 \
+    --hash=sha256:b5918ba197c951dec132b0c5929a00c0bf05d5942f590d3c10a807f6e15a57d3 \
+    --hash=sha256:b75c347eff42497452116ce05ef461822d97ce5b9ff8df6edacb8076092c855d \
+    --hash=sha256:c3b723df9087a9a9a840e263ebd9f88b64a12075d1bf2ea401a5a42f254f084d \
+    --hash=sha256:c934008c733b8bbea273ea308b73b3156f0181e5b72960790b09c18a2794fe1e \
+    --hash=sha256:d1478075142e83a5571782ad007fb201ed074bdeac7ebcc8890c71442e96adf7 \
+    --hash=sha256:d606a041c89c0a474a4702d532ab7e73a14fe35c8d427b972a625c8e46373668 \
+    --hash=sha256:db0dbfd2a6cdf3770aa60464d50333d8f3d9165b2f2671bcc299b72de5a6677b \
+    --hash=sha256:dbbd4aa20ca51e63b53bbde6a0fa4254b1aaabb74d2f542df7a7959feb1d760c \
+    --hash=sha256:dbc20dea3b9e27d0e66d74c42b2d0c1bed9c2ffe92adea33633e3bedeb5ac235 \
+    --hash=sha256:deeca1b5a931fdf0c2212c8a659ade6d3b1edc21f0914ce71ef24456ca7a6535 \
+    --hash=sha256:ed72cb3f45190874eb579c64fa92d9df74e98fd63e2be7f62bce5ace0ade61df \
+    --hash=sha256:ef8b27695c3d3dc78403c9a7d5e59a62d5464a7e1123b4e0042763f7104dc74f \
+    --hash=sha256:f12b1a9e332c01e09510586f8ca9b108fd631fd656af82e452d7315ef6df5f9f \
+    --hash=sha256:f4753e73e34c8d83221ba58f232433fca2748be8b18dbca02d242ed153945043 \
+    --hash=sha256:f8d68083e49e16b84734eb1a4dcae4259a75c90fb6e2251ab9a00b61120c06ab
+    # via
+    #   cmdstanpy
+    #   pmdarima
+    #   prophet
+    #   shap
+    #   statsmodels
+papermill==2.7.0 \
+    --hash=sha256:e1855e6670100a02bb4f8a6870484a5c10b84a8d2e49c49921c90209940c7514 \
+    --hash=sha256:ec10b37594a060662f57269e1ebd108c209d204450f00fdfeb70a1c7cfb7fbc8
+    # via -r requirements.in
+patsy==1.0.2 \
+    --hash=sha256:37bfddbc58fcf0362febb5f54f10743f8b21dd2aa73dec7e7ef59d1b02ae668a \
+    --hash=sha256:cdc995455f6233e90e22de72c37fcadb344e7586fb83f06696f54d92f8ce74c0
+    # via statsmodels
+pillow==12.2.0 \
+    --hash=sha256:00a2865911330191c0b818c59103b58a5e697cae67042366970a6b6f1b20b7f9 \
+    --hash=sha256:01afa7cf67f74f09523699b4e88c73fb55c13346d212a59a2db1f86b0a63e8c5 \
+    --hash=sha256:03e7e372d5240cc23e9f07deca4d775c0817bffc641b01e9c3af208dbd300987 \
+    --hash=sha256:03f6fab9219220f041c74aeaa2939ff0062bd5c364ba9ce037197f4c6d498cd9 \
+    --hash=sha256:042db20a421b9bafecc4b84a8b6e444686bd9d836c7fd24542db3e7df7baad9b \
+    --hash=sha256:0538bd5e05efec03ae613fd89c4ce0368ecd2ba239cc25b9f9be7ed426b0af1f \
+    --hash=sha256:0a34329707af4f73cf1782a36cd2289c0368880654a2c11f027bcee9052d35dd \
+    --hash=sha256:0c838a5125cee37e68edec915651521191cef1e6aa336b855f495766e77a366e \
+    --hash=sha256:144748b3af2d1b358d41286056d0003f47cb339b8c43a9ea42f5fea4d8c66b6e \
+    --hash=sha256:1610dd6c61621ae1cf811bef44d77e149ce3f7b95afe66a4512f8c59f25d9ebe \
+    --hash=sha256:1e1757442ed87f4912397c6d35a0db6a7b52592156014706f17658ff58bbf795 \
+    --hash=sha256:22db17c68434de69d8ecfc2fe821569195c0c373b25cccb9cbdacf2c6e53c601 \
+    --hash=sha256:25373b66e0dd5905ed63fa3cae13c82fbddf3079f2c8bf15c6fb6a35586324c1 \
+    --hash=sha256:2bb4a8d594eacdfc59d9e5ad972aa8afdd48d584ffd5f13a937a664c3e7db0ed \
+    --hash=sha256:2c727a6d53cb0018aadd8018c2b938376af27914a68a492f59dfcaca650d5eea \
+    --hash=sha256:2d192a155bbcec180f8564f693e6fd9bccff5a7af9b32e2e4bf8c9c69dbad6b5 \
+    --hash=sha256:2e589959f10d9824d39b350472b92f0ce3b443c0a3442ebf41c40cb8361c5b97 \
+    --hash=sha256:2e5a76d03a6c6dcef67edabda7a52494afa4035021a79c8558e14af25313d453 \
+    --hash=sha256:325ca0528c6788d2a6c3d40e3568639398137346c3d6e66bb61db96b96511c98 \
+    --hash=sha256:34c0d99ecccea270c04882cb3b86e7b57296079c9a4aff88cb3b33563d95afaa \
+    --hash=sha256:390ede346628ccc626e5730107cde16c42d3836b89662a115a921f28440e6a3b \
+    --hash=sha256:394167b21da716608eac917c60aa9b969421b5dcbbe02ae7f013e7b85811c69d \
+    --hash=sha256:3997232e10d2920a68d25191392e3a4487d8183039e1c74c2297f00ed1c50705 \
+    --hash=sha256:3adc9215e8be0448ed6e814966ecf3d9952f0ea40eb14e89a102b87f450660d8 \
+    --hash=sha256:3e080565d8d7c671db5802eedfb438e5565ffa40115216eabb8cd52d0ecce024 \
+    --hash=sha256:4a6c9fa44005fa37a91ebfc95d081e8079757d2e904b27103f4f5fa6f0bf78c0 \
+    --hash=sha256:4bfd07bc812fbd20395212969e41931001fd59eb55a60658b0e5710872e95286 \
+    --hash=sha256:4e6c62e9d237e9b65fac06857d511e90d8461a32adcc1b9065ea0c0fa3a28150 \
+    --hash=sha256:50d8520da2a6ce0af445fa6d648c4273c3eeefbc32d7ce049f22e8b5c3daecc2 \
+    --hash=sha256:51c4167c34b0d8ba05b547a3bb23578d0ba17b80a5593f93bd8ecb123dd336a3 \
+    --hash=sha256:56a3f9c60a13133a98ecff6197af34d7824de9b7b38c3654861a725c970c197b \
+    --hash=sha256:56b25336f502b6ed02e889f4ece894a72612fe885889a6e8c4c80239ff6e5f5f \
+    --hash=sha256:57850958fe9c751670e49b2cecf6294acc99e562531f4bd317fa5ddee2068463 \
+    --hash=sha256:58f62cc0f00fd29e64b29f4fd923ffdb3859c9f9e6105bfc37ba1d08994e8940 \
+    --hash=sha256:5c0a9f29ca8e79f09de89293f82fc9b0270bb4af1d58bc98f540cc4aedf03166 \
+    --hash=sha256:5cdfebd752ec52bf5bb4e35d9c64b40826bc5b40a13df7c3cda20a2c03a0f5ed \
+    --hash=sha256:5d04bfa02cc2d23b497d1e90a0f927070043f6cbf303e738300532379a4b4e0f \
+    --hash=sha256:5d2fd0fa6b5d9d1de415060363433f28da8b1526c1c129020435e186794b3795 \
+    --hash=sha256:62f5409336adb0663b7caa0da5c7d9e7bdbaae9ce761d34669420c2a801b2780 \
+    --hash=sha256:632ff19b2778e43162304d50da0181ce24ac5bb8180122cbe1bf4673428328c7 \
+    --hash=sha256:6562ace0d3fb5f20ed7290f1f929cae41b25ae29528f2af1722966a0a02e2aa1 \
+    --hash=sha256:673aa32138f3e7531ccdbca7b3901dba9b70940a19ccecc6a37c77d5fdeb05b5 \
+    --hash=sha256:6a6e67ea2e6feda684ed370f9a1c52e7a243631c025ba42149a2cc5934dec295 \
+    --hash=sha256:6a9adfc6d24b10f89588096364cc726174118c62130c817c2837c60cf08a392b \
+    --hash=sha256:6bb77b2dcb06b20f9f4b4a8454caa581cd4dd0643a08bacf821216a16d9c8354 \
+    --hash=sha256:6e6b2a0c538fc200b38ff9eb6628228b77908c319a005815f2dde585a0664b60 \
+    --hash=sha256:71cde9a1e1551df7d34a25462fc60325e8a11a82cc2e2f54578e5e9a1e153d65 \
+    --hash=sha256:7371b48c4fa448d20d2714c9a1f775a81155050d383333e0a6c15b1123dda005 \
+    --hash=sha256:766cef22385fa1091258ad7e6216792b156dc16d8d3fa607e7545b2b72061f1c \
+    --hash=sha256:7b14cc0106cd9aecda615dd6903840a058b4700fcb817687d0ee4fc8b6e389be \
+    --hash=sha256:7f84204dee22a783350679a0333981df803dac21a0190d706a50475e361c93f5 \
+    --hash=sha256:8023abc91fba39036dbce14a7d6535632f99c0b857807cbbbf21ecc9f4717f06 \
+    --hash=sha256:80b2da48193b2f33ed0c32c38140f9d3186583ce7d516526d462645fd98660ae \
+    --hash=sha256:8297651f5b5679c19968abefd6bb84d95fe30ef712eb1b2d9b2d31ca61267f4c \
+    --hash=sha256:88d387ff40b3ff7c274947ed3125dedf5262ec6919d83946753b5f3d7c67ea4c \
+    --hash=sha256:88ddbc66737e277852913bd1e07c150cc7bb124539f94c4e2df5344494e0a612 \
+    --hash=sha256:8bd7903a5f2a4545f6fd5935c90058b89d30045568985a71c79f5fd6edf9b91e \
+    --hash=sha256:8be29e59487a79f173507c30ddf57e733a357f67881430449bb32614075a40ab \
+    --hash=sha256:8c984051042858021a54926eb597d6ee3012393ce9c181814115df4c60b9a808 \
+    --hash=sha256:8cbeb542b2ebc6fcdacabf8aca8c1a97c9b3ad3927d46b8723f9d4f033288a0f \
+    --hash=sha256:8e9c4f5b3c546fa3458a29ab22646c1c6c787ea8f5ef51300e5a60300736905e \
+    --hash=sha256:90e6f81de50ad6b534cab6e5aef77ff6e37722b2f5d908686f4a5c9eba17a909 \
+    --hash=sha256:975385f4776fafde056abb318f612ef6285b10a1f12b8570f3647ad0d74b48ec \
+    --hash=sha256:9a8a34cc89c67a65ea7437ce257cea81a9dad65b29805f3ecee8c8fe8ff25ffe \
+    --hash=sha256:9aba9a17b623ef750a4d11b742cbafffeb48a869821252b30ee21b5e91392c50 \
+    --hash=sha256:9f08483a632889536b8139663db60f6724bfcb443c96f1b18855860d7d5c0fd4 \
+    --hash=sha256:a4e8f36e677d3336f35089648c8955c51c6d386a13cf6ee9c189c5f5bd713a9f \
+    --hash=sha256:a52edc8bfff4429aaabdf4d9ee0daadbbf8562364f940937b941f87a4290f5ff \
+    --hash=sha256:a830b1a40919539d07806aa58e1b114df53ddd43213d9c8b75847eee6c0182b5 \
+    --hash=sha256:aa88ccfe4e32d362816319ed727a004423aab09c5cea43c01a4b435643fa34eb \
+    --hash=sha256:af73337013e0b3b46f175e79492d96845b16126ddf79c438d7ea7ff27783a414 \
+    --hash=sha256:b1c1fbd8a5a1af3412a0810d060a78b5136ec0836c8a4ef9aa11807f2a22f4e1 \
+    --hash=sha256:b85f66ae9eb53e860a873b858b789217ba505e5e405a24b85c0464822fe88032 \
+    --hash=sha256:b86024e52a1b269467a802258c25521e6d742349d760728092e1bc2d135b4d76 \
+    --hash=sha256:bd9c0c7a0c681a347b3194c500cb1e6ca9cab053ea4d82a5cf45b6b754560136 \
+    --hash=sha256:bfa9c230d2fe991bed5318a5f119bd6780cda2915cca595393649fc118ab895e \
+    --hash=sha256:d362d1878f00c142b7e1a16e6e5e780f02be8195123f164edf7eddd911eefe7c \
+    --hash=sha256:d5d38f1411c0ed9f97bcb49b7bd59b6b7c314e0e27420e34d99d844b9ce3b6f3 \
+    --hash=sha256:dac8d77255a37e81a2efcbd1fc05f1c15ee82200e6c240d7e127e25e365c39ea \
+    --hash=sha256:dd025009355c926a84a612fecf58bb315a3f6814b17ead51a8e48d3823d9087f \
+    --hash=sha256:deede7c263feb25dba4e82ea23058a235dcc2fe1f6021025dc71f2b618e26104 \
+    --hash=sha256:e74473c875d78b8e9d5da2a70f7099549f9eb37ded4e2f6a463e60125bccd176 \
+    --hash=sha256:ee3120ae9dff32f121610bb08e4313be87e03efeadfc6c0d18f89127e24d0c24 \
+    --hash=sha256:eedf4b74eda2b5a4b2b2fb4c006d6295df3bf29e459e198c90ea48e130dc75c3 \
+    --hash=sha256:efd8c21c98c5cc60653bcb311bef2ce0401642b7ce9d09e03a7da87c878289d4 \
+    --hash=sha256:f1c943e96e85df3d3478f7b691f229887e143f81fedab9b20205349ab04d73ed \
+    --hash=sha256:f278f034eb75b4e8a13a54a876cc4a5ab39173d2cdd93a638e1b467fc545ac43 \
+    --hash=sha256:f3f40b3c5a968281fd507d519e444c35f0ff171237f4fdde090dd60699458421 \
+    --hash=sha256:f490f9368b6fc026f021db16d7ec2fbf7d89e2edb42e8ec09d2c60505f5729c7 \
+    --hash=sha256:fb043ee2f06b41473269765c2feae53fc2e2fbf96e5e22ca94fb5ad677856f06 \
+    --hash=sha256:fc3d34d4a8fbec3e88a79b92e5465e0f9b842b628675850d860b8bd300b159f5
+    # via matplotlib
+platformdirs==4.9.6 \
+    --hash=sha256:3bfa75b0ad0db84096ae777218481852c0ebc6c727b3168c1b9e0118e458cf0a \
+    --hash=sha256:e61adb1d5e5cb3441b4b7710bea7e4c12250ca49439228cc1021c00dcfac0917
+    # via
+    #   jupyter-core
+    #   python-discovery
+    #   virtualenv
+plotly==6.7.0 \
+    --hash=sha256:45eea0ff27e2a23ccd62776f77eb43aa1ca03df4192b76036e380bb479b892c6 \
+    --hash=sha256:ac8aca1c25c663a59b5b9140a549264a5badde2e057d79b8c772ae2920e32ff0
+    # via -r requirements.in
+pluggy==1.6.0 \
+    --hash=sha256:7dcc130b76258d33b90f61b658791dede3486c3e6bfb003ee5c9bfb396dd22f3 \
+    --hash=sha256:e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746
+    # via pytest
+pmdarima==2.1.1 \
+    --hash=sha256:1a315609437523ced314c86cffbcb5d957d3b8850e3c8a9bfdb51e93c5b6b597 \
+    --hash=sha256:30e417ead2aa21b0148d082a9b6a2b46c88fef6b8ed97fca9e8c796ee43e16be \
+    --hash=sha256:31f1a48517849fcd52a5844d6605f0c2acf0a8bf6fadffcc5fdabb08d8201328 \
+    --hash=sha256:320942588f7d32fb8b38fa648c46a60a4e43f87d1ceb722e796d4d456997069c \
+    --hash=sha256:32812a95237bb5f1b50fe630e71d4349141fd171193e8769b30b81989fecd5eb \
+    --hash=sha256:4218d71dbd2010d72bda00092b0e7d167d60d7ce1f44463a9a8869a2fae2eac1 \
+    --hash=sha256:4639c9438bcdef98e984fd9b55224a5bf61589a1f5ae3ad539ce5e9e28fdb564 \
+    --hash=sha256:512fa4c5c34328e0ec1658640c04f8af6eddccae784f28630afa8e4beacdffd3 \
+    --hash=sha256:57c20e85d97f639fa4376cef0a0d1a6ba12c11eb5629b0043267ec1d0d1c391d \
+    --hash=sha256:6e817db74d7c749d6c68fb5482b90255a3064bc924b18312d594de1bcbd03536 \
+    --hash=sha256:71eb1c5586f3f06e6ed9f3649c393ef02d039daa7bbf966793dc99977beb0254 \
+    --hash=sha256:750782537b7fbf09dc29f82c88d0c3afd97c0567eca0dc1054692b5996dea4cd \
+    --hash=sha256:76d1120cd0497c5c7e1cc566ff771d82b7059f9202c51fd60e932d7f525aa693 \
+    --hash=sha256:7e0080637d9d9a21687dec3062ad512f6ae1ee47abd9f47770d3782510321d8c \
+    --hash=sha256:7ffe658df9f6b2d60150d439001e95de1a82b6c0121174fd9d1a1a131b6bfb89 \
+    --hash=sha256:b038d14686a5af23e83c7ecc1cab0d2fa57c2445e1d0754d56ffdc6e85e9a955 \
+    --hash=sha256:b4df5236a8be6e4995cc922573a8cee93f306c1576681b290bbfda3d4c9f6c50 \
+    --hash=sha256:b8d2a0c0cd3f7ec90825fa25a917b5f66073de58033511de015a9e76e4e3d8f7 \
+    --hash=sha256:c2e74ff51489c5a68108422c0db77e298ec297abaa99ec3ae7729596ae5951c9 \
+    --hash=sha256:c8b2776edaedcc63ceddfcfb1e6240286b3d7f027500011fc6989764aebd0510 \
+    --hash=sha256:df15ae4c646865f66158b2552b30f069396af894bbf8c59afaa0329b021aaf42 \
+    --hash=sha256:e8148ff1f4cdb9a07164247eb3e6dddc1baef6e226d38528bd3fdf5d160f8dee \
+    --hash=sha256:ef25387a5ae2a1bf1a86d3d0a2009ee6d291b4129a5d578d8d42e3f18ae6c109 \
+    --hash=sha256:f2c639f114c247a90233ec9a8f076a65765cfc940440316525c44e8e581d5820 \
+    --hash=sha256:f68bd04ac170b0463de308b2b0dccae4696e113047caf078b17fa84273ece75a \
+    --hash=sha256:f80c1d4d9947d114807c49b0969e6cb0109c7d68917aaa1c5f1620694c40a33a
+    # via -r requirements.in
+pre-commit==4.6.0 \
+    --hash=sha256:718d2208cef53fdc38206e40524a6d4d9576d103eb16f0fec11c875e7716e9d9 \
+    --hash=sha256:e2cf246f7299edcabcf15f9b0571fdce06058527f0a06535068a86d38089f29b
+    # via -r requirements.in
+prophet==1.3.0 \
+    --hash=sha256:1f51922a0db9bae8af3e46e33b094487f1be0c96a373b47ec3ad041020adacd0 \
+    --hash=sha256:6790f9f06cc9e76d2f21c501f5889cf37f75917fba6859e196889dfde4bfec3b \
+    --hash=sha256:7ec252e898199a1965ca10db3ca625a4ec75e4e6f738d2b4108fe603666a9ef0 \
+    --hash=sha256:b65f189002a406413c58a28af40b6f2b240bba1ebf1158d204c46ebc570cd3c0 \
+    --hash=sha256:ed25f79e554d928b123cbf4f5a8a4e33bb003c7e26dcc2c8352e900f11f6b770 \
+    --hash=sha256:fe70571cbd051a8e1f6c5ff3a53215a6287820b7f2991df056406eefb4a615a7
+    # via -r requirements.in
+protobuf==7.34.1 \
+    --hash=sha256:34b84ce27680df7cca9f231043ada0daa55d0c44a2ddfaa58ec1d0d89d8bf60a \
+    --hash=sha256:403b093a6e28a960372b44e5eb081775c9b056e816a8029c61231743d63f881a \
+    --hash=sha256:5185e0e948d07abe94bb76ec9b8416b604cfe5da6f871d67aad30cbf24c3110b \
+    --hash=sha256:8ff40ce8cd688f7265326b38d5a1bed9bfdf5e6723d49961432f83e21d5713e4 \
+    --hash=sha256:9ce42245e704cc5027be797c1db1eb93184d44d1cdd71811fb2d9b25ad541280 \
+    --hash=sha256:bb3812cd53aefea2b028ef42bd780f5b96407247f20c6ef7c679807e9d188f11 \
+    --hash=sha256:d8b2cc79c4d8f62b293ad9b11ec3aebce9af481fa73e64556969f7345ebf9fc7 \
+    --hash=sha256:e97b55646e6ce5cbb0954a8c28cd39a5869b59090dfaa7df4598a7fba869468c
+    # via
+    #   kaggle
+    #   kagglesdk
+    #   onnxruntime
+pygments==2.20.0 \
+    --hash=sha256:6757cd03768053ff99f3039c1a36d6c0aa0b263438fcab17520b30a303a82b5f \
+    --hash=sha256:81a9e26dd42fd28a23a2d169d86d7ac03b46e2f8b59ed4698fb4785f946d0176
+    # via pytest
+pynndescent==0.6.0 \
+    --hash=sha256:7ffde0fb5b400741e055a9f7d377e3702e02250616834231f6c209e39aac24f5 \
+    --hash=sha256:dc8c74844e4c7f5cbd1e0cd6909da86fdc789e6ff4997336e344779c3d5538ef
+    # via umap-learn
+pyparsing==3.3.2 \
+    --hash=sha256:850ba148bd908d7e2411587e247a1e4f0327839c40e2e5e6d05a007ecc69911d \
+    --hash=sha256:c777f4d763f140633dcb6d8a3eda953bf7a214dc4eff598413c070bcdc117cbc
+    # via matplotlib
+pytest==9.0.3 \
+    --hash=sha256:2c5efc453d45394fdd706ade797c0a81091eccd1d6e4bccfcd476e2b8e0ab5d9 \
+    --hash=sha256:b86ada508af81d19edeb213c681b1d48246c1a91d304c6c81a427674c17eb91c
+    # via -r requirements.in
+python-dateutil==2.9.0.post0 \
+    --hash=sha256:37dd54208da7e1cd875388217d5e00ebd4179249f90fb72437e91a35459a0ad3 \
+    --hash=sha256:a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427
+    # via
+    #   holidays
+    #   jupyter-client
+    #   kaggle
+    #   matplotlib
+    #   pandas
+python-discovery==1.2.2 \
+    --hash=sha256:876e9c57139eb757cb5878cbdd9ae5379e5d96266c99ef731119e04fffe533bb \
+    --hash=sha256:e1ae95d9af875e78f15e19aed0c6137ab1bb49c200f21f5061786490c9585c7a
+    # via virtualenv
+python-slugify==8.0.4 \
+    --hash=sha256:276540b79961052b66b7d116620b36518847f52d5fd9e3a70164fc8c50faa6b8 \
+    --hash=sha256:59202371d1d05b54a9e7720c5e038f928f45daaffe41dd10822f3907b937c856
+    # via kaggle
+pyyaml==6.0.3 \
+    --hash=sha256:00c4bdeba853cc34e7dd471f16b4114f4162dc03e6b7afcc2128711f0eca823c \
+    --hash=sha256:0150219816b6a1fa26fb4699fb7daa9caf09eb1999f3b70fb6e786805e80375a \
+    --hash=sha256:02893d100e99e03eda1c8fd5c441d8c60103fd175728e23e431db1b589cf5ab3 \
+    --hash=sha256:02ea2dfa234451bbb8772601d7b8e426c2bfa197136796224e50e35a78777956 \
+    --hash=sha256:0f29edc409a6392443abf94b9cf89ce99889a1dd5376d94316ae5145dfedd5d6 \
+    --hash=sha256:10892704fc220243f5305762e276552a0395f7beb4dbf9b14ec8fd43b57f126c \
+    --hash=sha256:16249ee61e95f858e83976573de0f5b2893b3677ba71c9dd36b9cf8be9ac6d65 \
+    --hash=sha256:1d37d57ad971609cf3c53ba6a7e365e40660e3be0e5175fa9f2365a379d6095a \
+    --hash=sha256:1ebe39cb5fc479422b83de611d14e2c0d3bb2a18bbcb01f229ab3cfbd8fee7a0 \
+    --hash=sha256:214ed4befebe12df36bcc8bc2b64b396ca31be9304b8f59e25c11cf94a4c033b \
+    --hash=sha256:2283a07e2c21a2aa78d9c4442724ec1eb15f5e42a723b99cb3d822d48f5f7ad1 \
+    --hash=sha256:22ba7cfcad58ef3ecddc7ed1db3409af68d023b7f940da23c6c2a1890976eda6 \
+    --hash=sha256:27c0abcb4a5dac13684a37f76e701e054692a9b2d3064b70f5e4eb54810553d7 \
+    --hash=sha256:28c8d926f98f432f88adc23edf2e6d4921ac26fb084b028c733d01868d19007e \
+    --hash=sha256:2e71d11abed7344e42a8849600193d15b6def118602c4c176f748e4583246007 \
+    --hash=sha256:34d5fcd24b8445fadc33f9cf348c1047101756fd760b4dacb5c3e99755703310 \
+    --hash=sha256:37503bfbfc9d2c40b344d06b2199cf0e96e97957ab1c1b546fd4f87e53e5d3e4 \
+    --hash=sha256:3c5677e12444c15717b902a5798264fa7909e41153cdf9ef7ad571b704a63dd9 \
+    --hash=sha256:3ff07ec89bae51176c0549bc4c63aa6202991da2d9a6129d7aef7f1407d3f295 \
+    --hash=sha256:41715c910c881bc081f1e8872880d3c650acf13dfa8214bad49ed4cede7c34ea \
+    --hash=sha256:418cf3f2111bc80e0933b2cd8cd04f286338bb88bdc7bc8e6dd775ebde60b5e0 \
+    --hash=sha256:44edc647873928551a01e7a563d7452ccdebee747728c1080d881d68af7b997e \
+    --hash=sha256:4a2e8cebe2ff6ab7d1050ecd59c25d4c8bd7e6f400f5f82b96557ac0abafd0ac \
+    --hash=sha256:4ad1906908f2f5ae4e5a8ddfce73c320c2a1429ec52eafd27138b7f1cbe341c9 \
+    --hash=sha256:501a031947e3a9025ed4405a168e6ef5ae3126c59f90ce0cd6f2bfc477be31b7 \
+    --hash=sha256:5190d403f121660ce8d1d2c1bb2ef1bd05b5f68533fc5c2ea899bd15f4399b35 \
+    --hash=sha256:5498cd1645aa724a7c71c8f378eb29ebe23da2fc0d7a08071d89469bf1d2defb \
+    --hash=sha256:5cf4e27da7e3fbed4d6c3d8e797387aaad68102272f8f9752883bc32d61cb87b \
+    --hash=sha256:5e0b74767e5f8c593e8c9b5912019159ed0533c70051e9cce3e8b6aa699fcd69 \
+    --hash=sha256:5ed875a24292240029e4483f9d4a4b8a1ae08843b9c54f43fcc11e404532a8a5 \
+    --hash=sha256:5fcd34e47f6e0b794d17de1b4ff496c00986e1c83f7ab2fb8fcfe9616ff7477b \
+    --hash=sha256:5fdec68f91a0c6739b380c83b951e2c72ac0197ace422360e6d5a959d8d97b2c \
+    --hash=sha256:6344df0d5755a2c9a276d4473ae6b90647e216ab4757f8426893b5dd2ac3f369 \
+    --hash=sha256:64386e5e707d03a7e172c0701abfb7e10f0fb753ee1d773128192742712a98fd \
+    --hash=sha256:652cb6edd41e718550aad172851962662ff2681490a8a711af6a4d288dd96824 \
+    --hash=sha256:66291b10affd76d76f54fad28e22e51719ef9ba22b29e1d7d03d6777a9174198 \
+    --hash=sha256:66e1674c3ef6f541c35191caae2d429b967b99e02040f5ba928632d9a7f0f065 \
+    --hash=sha256:6adc77889b628398debc7b65c073bcb99c4a0237b248cacaf3fe8a557563ef6c \
+    --hash=sha256:79005a0d97d5ddabfeeea4cf676af11e647e41d81c9a7722a193022accdb6b7c \
+    --hash=sha256:7c6610def4f163542a622a73fb39f534f8c101d690126992300bf3207eab9764 \
+    --hash=sha256:7f047e29dcae44602496db43be01ad42fc6f1cc0d8cd6c83d342306c32270196 \
+    --hash=sha256:8098f252adfa6c80ab48096053f512f2321f0b998f98150cea9bd23d83e1467b \
+    --hash=sha256:850774a7879607d3a6f50d36d04f00ee69e7fc816450e5f7e58d7f17f1ae5c00 \
+    --hash=sha256:8d1fab6bb153a416f9aeb4b8763bc0f22a5586065f86f7664fc23339fc1c1fac \
+    --hash=sha256:8da9669d359f02c0b91ccc01cac4a67f16afec0dac22c2ad09f46bee0697eba8 \
+    --hash=sha256:8dc52c23056b9ddd46818a57b78404882310fb473d63f17b07d5c40421e47f8e \
+    --hash=sha256:9149cad251584d5fb4981be1ecde53a1ca46c891a79788c0df828d2f166bda28 \
+    --hash=sha256:93dda82c9c22deb0a405ea4dc5f2d0cda384168e466364dec6255b293923b2f3 \
+    --hash=sha256:96b533f0e99f6579b3d4d4995707cf36df9100d67e0c8303a0c55b27b5f99bc5 \
+    --hash=sha256:9c57bb8c96f6d1808c030b1687b9b5fb476abaa47f0db9c0101f5e9f394e97f4 \
+    --hash=sha256:9c7708761fccb9397fe64bbc0395abcae8c4bf7b0eac081e12b809bf47700d0b \
+    --hash=sha256:9f3bfb4965eb874431221a3ff3fdcddc7e74e3b07799e0e84ca4a0f867d449bf \
+    --hash=sha256:a33284e20b78bd4a18c8c2282d549d10bc8408a2a7ff57653c0cf0b9be0afce5 \
+    --hash=sha256:a80cb027f6b349846a3bf6d73b5e95e782175e52f22108cfa17876aaeff93702 \
+    --hash=sha256:b30236e45cf30d2b8e7b3e85881719e98507abed1011bf463a8fa23e9c3e98a8 \
+    --hash=sha256:b3bc83488de33889877a0f2543ade9f70c67d66d9ebb4ac959502e12de895788 \
+    --hash=sha256:b865addae83924361678b652338317d1bd7e79b1f4596f96b96c77a5a34b34da \
+    --hash=sha256:b8bb0864c5a28024fac8a632c443c87c5aa6f215c0b126c449ae1a150412f31d \
+    --hash=sha256:ba1cc08a7ccde2d2ec775841541641e4548226580ab850948cbfda66a1befcdc \
+    --hash=sha256:bdb2c67c6c1390b63c6ff89f210c8fd09d9a1217a465701eac7316313c915e4c \
+    --hash=sha256:c1ff362665ae507275af2853520967820d9124984e0f7466736aea23d8611fba \
+    --hash=sha256:c2514fceb77bc5e7a2f7adfaa1feb2fb311607c9cb518dbc378688ec73d8292f \
+    --hash=sha256:c3355370a2c156cffb25e876646f149d5d68f5e0a3ce86a5084dd0b64a994917 \
+    --hash=sha256:c458b6d084f9b935061bc36216e8a69a7e293a2f1e68bf956dcd9e6cbcd143f5 \
+    --hash=sha256:d0eae10f8159e8fdad514efdc92d74fd8d682c933a6dd088030f3834bc8e6b26 \
+    --hash=sha256:d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f \
+    --hash=sha256:ebc55a14a21cb14062aa4162f906cd962b28e2e9ea38f9b4391244cd8de4ae0b \
+    --hash=sha256:eda16858a3cab07b80edaf74336ece1f986ba330fdb8ee0d6c0d68fe82bc96be \
+    --hash=sha256:ee2922902c45ae8ccada2c5b501ab86c36525b883eff4255313a253a3160861c \
+    --hash=sha256:efd7b85f94a6f21e4932043973a7ba2613b059c4a000551892ac9f1d11f5baf3 \
+    --hash=sha256:f7057c9a337546edc7973c0d3ba84ddcdf0daa14533c2065749c9075001090e6 \
+    --hash=sha256:fa160448684b4e94d80416c0fa4aac48967a969efe22931448d853ada8baf926 \
+    --hash=sha256:fc09d0aa354569bc501d4e787133afc08552722d3ab34836a80547331bb5d4a0
+    # via
+    #   jupytext
+    #   optuna
+    #   papermill
+    #   pre-commit
+pyzmq==27.1.0 \
+    --hash=sha256:01c0e07d558b06a60773744ea6251f769cd79a41a97d11b8bf4ab8f034b0424d \
+    --hash=sha256:01f9437501886d3a1dd4b02ef59fb8cc384fa718ce066d52f175ee49dd5b7ed8 \
+    --hash=sha256:03ff0b279b40d687691a6217c12242ee71f0fba28bf8626ff50e3ef0f4410e1e \
+    --hash=sha256:05b12f2d32112bf8c95ef2e74ec4f1d4beb01f8b5e703b38537f8849f92cb9ba \
+    --hash=sha256:0790a0161c281ca9723f804871b4027f2e8b5a528d357c8952d08cd1a9c15581 \
+    --hash=sha256:08363b2011dec81c354d694bdecaef4770e0ae96b9afea70b3f47b973655cc05 \
+    --hash=sha256:08e90bb4b57603b84eab1d0ca05b3bbb10f60c1839dc471fc1c9e1507bef3386 \
+    --hash=sha256:0c996ded912812a2fcd7ab6574f4ad3edc27cb6510349431e4930d4196ade7db \
+    --hash=sha256:0de3028d69d4cdc475bfe47a6128eb38d8bc0e8f4d69646adfbcd840facbac28 \
+    --hash=sha256:15c8bd0fe0dabf808e2d7a681398c4e5ded70a551ab47482067a572c054c8e2e \
+    --hash=sha256:1779be8c549e54a1c38f805e56d2a2e5c009d26de10921d7d51cfd1c8d4632ea \
+    --hash=sha256:18339186c0ed0ce5835f2656cdfb32203125917711af64da64dbaa3d949e5a1b \
+    --hash=sha256:18770c8d3563715387139060d37859c02ce40718d1faf299abddcdcc6a649066 \
+    --hash=sha256:190cbf120fbc0fc4957b56866830def56628934a9d112aec0e2507aa6a032b97 \
+    --hash=sha256:19c9468ae0437f8074af379e986c5d3d7d7bfe033506af442e8c879732bedbe0 \
+    --hash=sha256:1c179799b118e554b66da67d88ed66cd37a169f1f23b5d9f0a231b4e8d44a113 \
+    --hash=sha256:1f0b2a577fd770aa6f053211a55d1c47901f4d537389a034c690291485e5fe92 \
+    --hash=sha256:1f8426a01b1c4098a750973c37131cf585f61c7911d735f729935a0c701b68d3 \
+    --hash=sha256:226b091818d461a3bef763805e75685e478ac17e9008f49fce2d3e52b3d58b86 \
+    --hash=sha256:250e5436a4ba13885494412b3da5d518cd0d3a278a1ae640e113c073a5f88edd \
+    --hash=sha256:346e9ba4198177a07e7706050f35d733e08c1c1f8ceacd5eb6389d653579ffbc \
+    --hash=sha256:3837439b7f99e60312f0c926a6ad437b067356dc2bc2ec96eb395fd0fe804233 \
+    --hash=sha256:3970778e74cb7f85934d2b926b9900e92bfe597e62267d7499acc39c9c28e345 \
+    --hash=sha256:43ad9a73e3da1fab5b0e7e13402f0b2fb934ae1c876c51d0afff0e7c052eca31 \
+    --hash=sha256:448f9cb54eb0cee4732b46584f2710c8bc178b0e5371d9e4fc8125201e413a74 \
+    --hash=sha256:452631b640340c928fa343801b0d07eb0c3789a5ffa843f6e1a9cee0ba4eb4fc \
+    --hash=sha256:49d3980544447f6bd2968b6ac913ab963a49dcaa2d4a2990041f16057b04c429 \
+    --hash=sha256:4a19387a3dddcc762bfd2f570d14e2395b2c9701329b266f83dd87a2b3cbd381 \
+    --hash=sha256:4c618fbcd069e3a29dcd221739cacde52edcc681f041907867e0f5cc7e85f172 \
+    --hash=sha256:50081a4e98472ba9f5a02850014b4c9b629da6710f8f14f3b15897c666a28f1b \
+    --hash=sha256:507b6f430bdcf0ee48c0d30e734ea89ce5567fd7b8a0f0044a369c176aa44556 \
+    --hash=sha256:508e23ec9bc44c0005c4946ea013d9317ae00ac67778bd47519fdf5a0e930ff4 \
+    --hash=sha256:510869f9df36ab97f89f4cff9d002a89ac554c7ac9cadd87d444aa4cf66abd27 \
+    --hash=sha256:53b40f8ae006f2734ee7608d59ed661419f087521edbfc2149c3932e9c14808c \
+    --hash=sha256:544b4e3b7198dde4a62b8ff6685e9802a9a1ebf47e77478a5eb88eca2a82f2fd \
+    --hash=sha256:5bbf8d3630bf96550b3be8e1fc0fea5cbdc8d5466c1192887bd94869da17a63e \
+    --hash=sha256:677e744fee605753eac48198b15a2124016c009a11056f93807000ab11ce6526 \
+    --hash=sha256:6bb54ca21bcfe361e445256c15eedf083f153811c37be87e0514934d6913061e \
+    --hash=sha256:6df079c47d5902af6db298ec92151db82ecb557af663098b92f2508c398bb54f \
+    --hash=sha256:6f3afa12c392f0a44a2414056d730eebc33ec0926aae92b5ad5cf26ebb6cc128 \
+    --hash=sha256:7200bb0f03345515df50d99d3db206a0a6bee1955fbb8c453c76f5bf0e08fb96 \
+    --hash=sha256:722ea791aa233ac0a819fc2c475e1292c76930b31f1d828cb61073e2fe5e208f \
+    --hash=sha256:726b6a502f2e34c6d2ada5e702929586d3ac948a4dbbb7fed9854ec8c0466027 \
+    --hash=sha256:753d56fba8f70962cd8295fb3edb40b9b16deaa882dd2b5a3a2039f9ff7625aa \
+    --hash=sha256:75a2f36223f0d535a0c919e23615fc85a1e23b71f40c7eb43d7b1dedb4d8f15f \
+    --hash=sha256:7be883ff3d722e6085ee3f4afc057a50f7f2e0c72d289fd54df5706b4e3d3a50 \
+    --hash=sha256:7ccc0700cfdf7bd487bea8d850ec38f204478681ea02a582a8da8171b7f90a1c \
+    --hash=sha256:8085a9fba668216b9b4323be338ee5437a235fe275b9d1610e422ccc279733e2 \
+    --hash=sha256:80d834abee71f65253c91540445d37c4c561e293ba6e741b992f20a105d69146 \
+    --hash=sha256:849ca054d81aa1c175c49484afaaa5db0622092b5eccb2055f9f3bb8f703782d \
+    --hash=sha256:90e6e9441c946a8b0a667356f7078d96411391a3b8f80980315455574177ec97 \
+    --hash=sha256:93ad4b0855a664229559e45c8d23797ceac03183c7b6f5b4428152a6b06684a5 \
+    --hash=sha256:9541c444cfe1b1c0156c5c86ece2bb926c7079a18e7b47b0b1b3b1b875e5d098 \
+    --hash=sha256:96c71c32fff75957db6ae33cd961439f386505c6e6b377370af9b24a1ef9eafb \
+    --hash=sha256:9a916f76c2ab8d045b19f2286851a38e9ac94ea91faf65bd64735924522a8b32 \
+    --hash=sha256:9c1790386614232e1b3a40a958454bdd42c6d1811837b15ddbb052a032a43f62 \
+    --hash=sha256:9ce490cf1d2ca2ad84733aa1d69ce6855372cb5ce9223802450c9b2a7cba0ccf \
+    --hash=sha256:a1aa0ee920fb3825d6c825ae3f6c508403b905b698b6460408ebd5bb04bbb312 \
+    --hash=sha256:a5b42d7a0658b515319148875fcb782bbf118dd41c671b62dae33666c2213bda \
+    --hash=sha256:ac0765e3d44455adb6ddbf4417dcce460fc40a05978c08efdf2948072f6db540 \
+    --hash=sha256:ac25465d42f92e990f8d8b0546b01c391ad431c3bf447683fdc40565941d0604 \
+    --hash=sha256:ad68808a61cbfbbae7ba26d6233f2a4aa3b221de379ce9ee468aa7a83b9c36b0 \
+    --hash=sha256:add071b2d25f84e8189aaf0882d39a285b42fa3853016ebab234a5e78c7a43db \
+    --hash=sha256:b1267823d72d1e40701dcba7edc45fd17f71be1285557b7fe668887150a14b78 \
+    --hash=sha256:b2e592db3a93128daf567de9650a2f3859017b3f7a66bc4ed6e4779d6034976f \
+    --hash=sha256:b721c05d932e5ad9ff9344f708c96b9e1a485418c6618d765fca95d4daacfbef \
+    --hash=sha256:bafcb3dd171b4ae9f19ee6380dfc71ce0390fefaf26b504c0e5f628d7c8c54f2 \
+    --hash=sha256:bd67e7c8f4654bef471c0b1ca6614af0b5202a790723a58b79d9584dc8022a78 \
+    --hash=sha256:bf7b38f9fd7b81cb6d9391b2946382c8237fd814075c6aa9c3b746d53076023b \
+    --hash=sha256:c0bb87227430ee3aefcc0ade2088100e528d5d3298a0a715a64f3d04c60ba02f \
+    --hash=sha256:c17e03cbc9312bee223864f1a2b13a99522e0dc9f7c5df0177cd45210ac286e6 \
+    --hash=sha256:c65047adafe573ff023b3187bb93faa583151627bc9c51fc4fb2c561ed689d39 \
+    --hash=sha256:c895a6f35476b0c3a54e3eb6ccf41bf3018de937016e6e18748317f25d4e925f \
+    --hash=sha256:c9f7f6e13dff2e44a6afeaf2cf54cee5929ad64afaf4d40b50f93c58fc687355 \
+    --hash=sha256:ce980af330231615756acd5154f29813d553ea555485ae712c491cd483df6b7a \
+    --hash=sha256:cedc4c68178e59a4046f97eca31b148ddcf51e88677de1ef4e78cf06c5376c9a \
+    --hash=sha256:cf44a7763aea9298c0aa7dbf859f87ed7012de8bda0f3977b6fb1d96745df856 \
+    --hash=sha256:d54530c8c8b5b8ddb3318f481297441af102517602b569146185fa10b63f4fa9 \
+    --hash=sha256:da96ecdcf7d3919c3be2de91a8c513c186f6762aa6cf7c01087ed74fad7f0968 \
+    --hash=sha256:dc5dbf68a7857b59473f7df42650c621d7e8923fb03fa74a526890f4d33cc4d7 \
+    --hash=sha256:dd2fec2b13137416a1c5648b7009499bcc8fea78154cd888855fa32514f3dad1 \
+    --hash=sha256:df7cd397ece96cf20a76fae705d40efbab217d217897a5053267cd88a700c266 \
+    --hash=sha256:e2687c2d230e8d8584fbea433c24382edfeda0c60627aca3446aa5e58d5d1831 \
+    --hash=sha256:e30a74a39b93e2e1591b58eb1acef4902be27c957a8720b0e368f579b82dc22f \
+    --hash=sha256:e343d067f7b151cfe4eb3bb796a7752c9d369eed007b91231e817071d2c2fec7 \
+    --hash=sha256:e829529fcaa09937189178115c49c504e69289abd39967cd8a4c215761373394 \
+    --hash=sha256:eca6b47df11a132d1745eb3b5b5e557a7dae2c303277aa0e69c6ba91b8736e07 \
+    --hash=sha256:f30f395a9e6fbca195400ce833c731e7b64c3919aa481af4d88c3759e0cb7496 \
+    --hash=sha256:f328d01128373cb6763823b2b4e7f73bdf767834268c565151eacb3b7a392f90 \
+    --hash=sha256:f605d884e7c8be8fe1aa94e0a783bf3f591b84c24e4bc4f3e7564c82ac25e271 \
+    --hash=sha256:fbb4f2400bfda24f12f009cba62ad5734148569ff4949b1b6ec3b519444342e6 \
+    --hash=sha256:ff8d114d14ac671d88c89b9224c63d6c4e5a613fe8acd5594ce53d752a3aafe9
+    # via jupyter-client
+referencing==0.37.0 \
+    --hash=sha256:381329a9f99628c9069361716891d34ad94af76e461dcb0335825aecc7692231 \
+    --hash=sha256:44aefc3142c5b842538163acb373e24cce6632bd54bdb01b21ad5863489f50d8
+    # via
+    #   jsonschema
+    #   jsonschema-specifications
+requests==2.33.1 \
+    --hash=sha256:18817f8c57c6263968bc123d237e3b8b08ac046f5456bd1e307ee8f4250d3517 \
+    --hash=sha256:4e6d1ef462f3626a1f0a0a9c42dd93c63bad33f9f1c1937509b8c5c8718ab56a
+    # via
+    #   kaggle
+    #   kagglesdk
+    #   papermill
+rpds-py==0.30.0 \
+    --hash=sha256:07ae8a593e1c3c6b82ca3292efbe73c30b61332fd612e05abee07c79359f292f \
+    --hash=sha256:0a59119fc6e3f460315fe9d08149f8102aa322299deaa5cab5b40092345c2136 \
+    --hash=sha256:0c0e95f6819a19965ff420f65578bacb0b00f251fefe2c8b23347c37174271f3 \
+    --hash=sha256:0d08f00679177226c4cb8c5265012eea897c8ca3b93f429e546600c971bcbae7 \
+    --hash=sha256:0ed177ed9bded28f8deb6ab40c183cd1192aa0de40c12f38be4d59cd33cb5c65 \
+    --hash=sha256:12f90dd7557b6bd57f40abe7747e81e0c0b119bef015ea7726e69fe550e394a4 \
+    --hash=sha256:1726859cd0de969f88dc8673bdd954185b9104e05806be64bcd87badbe313169 \
+    --hash=sha256:1ab5b83dbcf55acc8b08fc62b796ef672c457b17dbd7820a11d6c52c06839bdf \
+    --hash=sha256:1b151685b23929ab7beec71080a8889d4d6d9fa9a983d213f07121205d48e2c4 \
+    --hash=sha256:1f3587eb9b17f3789ad50824084fa6f81921bbf9a795826570bda82cb3ed91f2 \
+    --hash=sha256:250fa00e9543ac9b97ac258bd37367ff5256666122c2d0f2bc97577c60a1818c \
+    --hash=sha256:2771c6c15973347f50fece41fc447c054b7ac2ae0502388ce3b6738cd366e3d4 \
+    --hash=sha256:27f4b0e92de5bfbc6f86e43959e6edd1425c33b5e69aab0984a72047f2bcf1e3 \
+    --hash=sha256:2e6ecb5a5bcacf59c3f912155044479af1d0b6681280048b338b28e364aca1f6 \
+    --hash=sha256:32c8528634e1bf7121f3de08fa85b138f4e0dc47657866630611b03967f041d7 \
+    --hash=sha256:33f559f3104504506a44bb666b93a33f5d33133765b0c216a5bf2f1e1503af89 \
+    --hash=sha256:3896fa1be39912cf0757753826bc8bdc8ca331a28a7c4ae46b7a21280b06bb85 \
+    --hash=sha256:389a2d49eded1896c3d48b0136ead37c48e221b391c052fba3f4055c367f60a6 \
+    --hash=sha256:39c02563fc592411c2c61d26b6c5fe1e51eaa44a75aa2c8735ca88b0d9599daa \
+    --hash=sha256:3adbb8179ce342d235c31ab8ec511e66c73faa27a47e076ccc92421add53e2bb \
+    --hash=sha256:3d4a69de7a3e50ffc214ae16d79d8fbb0922972da0356dcf4d0fdca2878559c6 \
+    --hash=sha256:3e62880792319dbeb7eb866547f2e35973289e7d5696c6e295476448f5b63c87 \
+    --hash=sha256:3e8eeb0544f2eb0d2581774be4c3410356eba189529a6b3e36bbbf9696175856 \
+    --hash=sha256:422c3cb9856d80b09d30d2eb255d0754b23e090034e1deb4083f8004bd0761e4 \
+    --hash=sha256:4559c972db3a360808309e06a74628b95eaccbf961c335c8fe0d590cf587456f \
+    --hash=sha256:46e83c697b1f1c72b50e5ee5adb4353eef7406fb3f2043d64c33f20ad1c2fc53 \
+    --hash=sha256:47b0ef6231c58f506ef0b74d44e330405caa8428e770fec25329ed2cb971a229 \
+    --hash=sha256:47e77dc9822d3ad616c3d5759ea5631a75e5809d5a28707744ef79d7a1bcfcad \
+    --hash=sha256:47f236970bccb2233267d89173d3ad2703cd36a0e2a6e92d0560d333871a3d23 \
+    --hash=sha256:47f9a91efc418b54fb8190a6b4aa7813a23fb79c51f4bb84e418f5476c38b8db \
+    --hash=sha256:495aeca4b93d465efde585977365187149e75383ad2684f81519f504f5c13038 \
+    --hash=sha256:4c5f36a861bc4b7da6516dbdf302c55313afa09b81931e8280361a4f6c9a2d27 \
+    --hash=sha256:4cc2206b76b4f576934f0ed374b10d7ca5f457858b157ca52064bdfc26b9fc00 \
+    --hash=sha256:4e7fc54e0900ab35d041b0601431b0a0eb495f0851a0639b6ef90f7741b39a18 \
+    --hash=sha256:51a1234d8febafdfd33a42d97da7a43f5dcb120c1060e352a3fbc0c6d36e2083 \
+    --hash=sha256:55f66022632205940f1827effeff17c4fa7ae1953d2b74a8581baaefb7d16f8c \
+    --hash=sha256:58edca431fb9b29950807e301826586e5bbf24163677732429770a697ffe6738 \
+    --hash=sha256:5965af57d5848192c13534f90f9dd16464f3c37aaf166cc1da1cae1fd5a34898 \
+    --hash=sha256:5ba103fb455be00f3b1c2076c9d4264bfcb037c976167a6047ed82f23153f02e \
+    --hash=sha256:5d4c2aa7c50ad4728a094ebd5eb46c452e9cb7edbfdb18f9e1221f597a73e1e7 \
+    --hash=sha256:61046904275472a76c8c90c9ccee9013d70a6d0f73eecefd38c1ae7c39045a08 \
+    --hash=sha256:613aa4771c99f03346e54c3f038e4cc574ac09a3ddfb0e8878487335e96dead6 \
+    --hash=sha256:626a7433c34566535b6e56a1b39a7b17ba961e97ce3b80ec62e6f1312c025551 \
+    --hash=sha256:669b1805bd639dd2989b281be2cfd951c6121b65e729d9b843e9639ef1fd555e \
+    --hash=sha256:679ae98e00c0e8d68a7fda324e16b90fd5260945b45d3b824c892cec9eea3288 \
+    --hash=sha256:67b02ec25ba7a9e8fa74c63b6ca44cf5707f2fbfadae3ee8e7494297d56aa9df \
+    --hash=sha256:68f19c879420aa08f61203801423f6cd5ac5f0ac4ac82a2368a9fcd6a9a075e0 \
+    --hash=sha256:692bef75a5525db97318e8cd061542b5a79812d711ea03dbc1f6f8dbb0c5f0d2 \
+    --hash=sha256:6abc8880d9d036ecaafe709079969f56e876fcf107f7a8e9920ba6d5a3878d05 \
+    --hash=sha256:6bdfdb946967d816e6adf9a3d8201bfad269c67efe6cefd7093ef959683c8de0 \
+    --hash=sha256:6de2a32a1665b93233cde140ff8b3467bdb9e2af2b91079f0333a0974d12d464 \
+    --hash=sha256:73c67f2db7bc334e518d097c6d1e6fed021bbc9b7d678d6cc433478365d1d5f5 \
+    --hash=sha256:74a3243a411126362712ee1524dfc90c650a503502f135d54d1b352bd01f2404 \
+    --hash=sha256:76fec018282b4ead0364022e3c54b60bf368b9d926877957a8624b58419169b7 \
+    --hash=sha256:7c64d38fb49b6cdeda16ab49e35fe0da2e1e9b34bc38bd78386530f218b37139 \
+    --hash=sha256:7cee9c752c0364588353e627da8a7e808a66873672bcb5f52890c33fd965b394 \
+    --hash=sha256:7e6ecfcb62edfd632e56983964e6884851786443739dbfe3582947e87274f7cb \
+    --hash=sha256:806f36b1b605e2d6a72716f321f20036b9489d29c51c91f4dd29a3e3afb73b15 \
+    --hash=sha256:858738e9c32147f78b3ac24dc0edb6610000e56dc0f700fd5f651d0a0f0eb9ff \
+    --hash=sha256:8d6d1cc13664ec13c1b84241204ff3b12f9bb82464b8ad6e7a5d3486975c2eed \
+    --hash=sha256:9027da1ce107104c50c81383cae773ef5c24d296dd11c99e2629dbd7967a20c6 \
+    --hash=sha256:922e10f31f303c7c920da8981051ff6d8c1a56207dbdf330d9047f6d30b70e5e \
+    --hash=sha256:945dccface01af02675628334f7cf49c2af4c1c904748efc5cf7bbdf0b579f95 \
+    --hash=sha256:946fe926af6e44f3697abbc305ea168c2c31d3e3ef1058cf68f379bf0335a78d \
+    --hash=sha256:95f0802447ac2d10bcc69f6dc28fe95fdf17940367b21d34e34c737870758950 \
+    --hash=sha256:9854cf4f488b3d57b9aaeb105f06d78e5529d3145b1e4a41750167e8c213c6d3 \
+    --hash=sha256:993914b8e560023bc0a8bf742c5f303551992dcb85e247b1e5c7f4a7d145bda5 \
+    --hash=sha256:99b47d6ad9a6da00bec6aabe5a6279ecd3c06a329d4aa4771034a21e335c3a97 \
+    --hash=sha256:9a4e86e34e9ab6b667c27f3211ca48f73dba7cd3d90f8d5b11be56e5dbc3fb4e \
+    --hash=sha256:9cf69cdda1f5968a30a359aba2f7f9aa648a9ce4b580d6826437f2b291cfc86e \
+    --hash=sha256:a090322ca841abd453d43456ac34db46e8b05fd9b3b4ac0c78bcde8b089f959b \
+    --hash=sha256:a1010ed9524c73b94d15919ca4d41d8780980e1765babf85f9a2f90d247153dd \
+    --hash=sha256:a161f20d9a43006833cd7068375a94d035714d73a172b681d8881820600abfad \
+    --hash=sha256:a1d0bc22a7cdc173fedebb73ef81e07faef93692b8c1ad3733b67e31e1b6e1b8 \
+    --hash=sha256:a2bffea6a4ca9f01b3f8e548302470306689684e61602aa3d141e34da06cf425 \
+    --hash=sha256:a452763cc5198f2f98898eb98f7569649fe5da666c2dc6b5ddb10fde5a574221 \
+    --hash=sha256:a4796a717bf12b9da9d3ad002519a86063dcac8988b030e405704ef7d74d2d9d \
+    --hash=sha256:a51033ff701fca756439d641c0ad09a41d9242fa69121c7d8769604a0a629825 \
+    --hash=sha256:a8fa71a2e078c527c3e9dc9fc5a98c9db40bcc8a92b4e8858e36d329f8684b51 \
+    --hash=sha256:ac37f9f516c51e5753f27dfdef11a88330f04de2d564be3991384b2f3535d02e \
+    --hash=sha256:ac98b175585ecf4c0348fd7b29c3864bda53b805c773cbf7bfdaffc8070c976f \
+    --hash=sha256:acd7eb3f4471577b9b5a41baf02a978e8bdeb08b4b355273994f8b87032000a8 \
+    --hash=sha256:ad1fa8db769b76ea911cb4e10f049d80bf518c104f15b3edb2371cc65375c46f \
+    --hash=sha256:b40fb160a2db369a194cb27943582b38f79fc4887291417685f3ad693c5a1d5d \
+    --hash=sha256:b4dc1a6ff022ff85ecafef7979a2c6eb423430e05f1165d6688234e62ba99a07 \
+    --hash=sha256:ba3af48635eb83d03f6c9735dfb21785303e73d22ad03d489e88adae6eab8877 \
+    --hash=sha256:ba81a9203d07805435eb06f536d95a266c21e5b2dfbf6517748ca40c98d19e31 \
+    --hash=sha256:c2262bdba0ad4fc6fb5545660673925c2d2a5d9e2e0fb603aad545427be0fc58 \
+    --hash=sha256:c77afbd5f5250bf27bf516c7c4a016813eb2d3e116139aed0096940c5982da94 \
+    --hash=sha256:ca28829ae5f5d569bb62a79512c842a03a12576375d5ece7d2cadf8abe96ec28 \
+    --hash=sha256:cdc62c8286ba9bf7f47befdcea13ea0e26bf294bda99758fd90535cbaf408000 \
+    --hash=sha256:d948b135c4693daff7bc2dcfc4ec57237a29bd37e60c2fabf5aff2bbacf3e2f1 \
+    --hash=sha256:d96c2086587c7c30d44f31f42eae4eac89b60dabbac18c7669be3700f13c3ce1 \
+    --hash=sha256:d9a0ca5da0386dee0655b4ccdf46119df60e0f10da268d04fe7cc87886872ba7 \
+    --hash=sha256:da279aa314f00acbb803da1e76fa18666778e8a8f83484fba94526da5de2cba7 \
+    --hash=sha256:dbd936cde57abfee19ab3213cf9c26be06d60750e60a8e4dd85d1ab12c8b1f40 \
+    --hash=sha256:dc4f992dfe1e2bc3ebc7444f6c7051b4bc13cd8e33e43511e8ffd13bf407010d \
+    --hash=sha256:dc824125c72246d924f7f796b4f63c1e9dc810c7d9e2355864b3c3a73d59ade0 \
+    --hash=sha256:dd8ff7cf90014af0c0f787eea34794ebf6415242ee1d6fa91eaba725cc441e84 \
+    --hash=sha256:dea5b552272a944763b34394d04577cf0f9bd013207bc32323b5a89a53cf9c2f \
+    --hash=sha256:dff13836529b921e22f15cb099751209a60009731a68519630a24d61f0b1b30a \
+    --hash=sha256:e0b65193a413ccc930671c55153a03ee57cecb49e6227204b04fae512eb657a7 \
+    --hash=sha256:e5d3e6b26f2c785d65cc25ef1e5267ccbe1b069c5c21b8cc724efee290554419 \
+    --hash=sha256:e7536cd91353c5273434b4e003cbda89034d67e7710eab8761fd918ec6c69cf8 \
+    --hash=sha256:eb0b93f2e5c2189ee831ee43f156ed34e2a89a78a66b98cadad955972548be5a \
+    --hash=sha256:eb2c4071ab598733724c08221091e8d80e89064cd472819285a9ab0f24bcedb9 \
+    --hash=sha256:ec7c4490c672c1a0389d319b3a9cfcd098dcdc4783991553c332a15acf7249be \
+    --hash=sha256:ee454b2a007d57363c2dfd5b6ca4a5d7e2c518938f8ed3b706e37e5d470801ed \
+    --hash=sha256:ee6af14263f25eedc3bb918a3c04245106a42dfd4f5c2285ea6f997b1fc3f89a \
+    --hash=sha256:f14fc5df50a716f7ece6a80b6c78bb35ea2ca47c499e422aa4463455dd96d56d \
+    --hash=sha256:f207f69853edd6f6700b86efb84999651baf3789e78a466431df1331608e5324 \
+    --hash=sha256:f251c812357a3fed308d684a5079ddfb9d933860fc6de89f2b7ab00da481e65f \
+    --hash=sha256:f83424d738204d9770830d35290ff3273fbb02b41f919870479fab14b9d303b2 \
+    --hash=sha256:f8d1736cfb49381ba528cd5baa46f82fdc65c06e843dab24dd70b63d09121b3f \
+    --hash=sha256:fe5fa731a1fa8a0a56b0977413f8cacac1768dad38d16b3a296712709476fbd5
+    # via
+    #   jsonschema
+    #   referencing
+scikit-learn==1.8.0 \
+    --hash=sha256:00d6f1d66fbcf4eba6e356e1420d33cc06c70a45bb1363cd6f6a8e4ebbbdece2 \
+    --hash=sha256:0d6ae97234d5d7079dc0040990a6f7aeb97cb7fa7e8945f1999a429b23569e0a \
+    --hash=sha256:146b4d36f800c013d267b29168813f7a03a43ecd2895d04861f1240b564421da \
+    --hash=sha256:15fc3b5d19cc2be65404786857f2e13c70c83dd4782676dd6814e3b89dc8f5b9 \
+    --hash=sha256:2838551e011a64e3053ad7618dda9310175f7515f1742fa2d756f7c874c05961 \
+    --hash=sha256:29ffc74089f3d5e87dfca4c2c8450f88bdc61b0fc6ed5d267f3988f19a1309f6 \
+    --hash=sha256:2de443b9373b3b615aec1bb57f9baa6bb3a9bd093f1269ba95c17d870422b271 \
+    --hash=sha256:35c007dedb2ffe38fe3ee7d201ebac4a2deccd2408e8621d53067733e3c74809 \
+    --hash=sha256:3bad7565bc9cf37ce19a7c0d107742b320c1285df7aab1a6e2d28780df167242 \
+    --hash=sha256:4496bb2cf7a43ce1a2d7524a79e40bc5da45cf598dbf9545b7e8316ccba47bb4 \
+    --hash=sha256:4511be56637e46c25721e83d1a9cea9614e7badc7040c4d573d75fbe257d6fd7 \
+    --hash=sha256:5025ce924beccb28298246e589c691fe1b8c1c96507e6d27d12c5fadd85bfd76 \
+    --hash=sha256:56079a99c20d230e873ea40753102102734c5953366972a71d5cb39a32bc40c6 \
+    --hash=sha256:5e30adb87f0cc81c7690a84f7932dd66be5bac57cfe16b91cb9151683a4a2d3b \
+    --hash=sha256:5fb63362b5a7ddab88e52b6dbb47dac3fd7dafeee740dc6c8d8a446ddedade8e \
+    --hash=sha256:6b595b07a03069a2b1740dc08c2299993850ea81cce4fe19b2421e0c970de6b7 \
+    --hash=sha256:72358cce49465d140cc4e7792015bb1f0296a9742d5622c67e31399b75468b9e \
+    --hash=sha256:74b66d8689d52ed04c271e1329f0c61635bcaf5b926db9b12d58914cdc01fe57 \
+    --hash=sha256:7cc267b6108f0a1499a734167282c00c4ebf61328566b55ef262d48e9849c735 \
+    --hash=sha256:80832434a6cc114f5219211eec13dcbc16c2bac0e31ef64c6d346cde3cf054cb \
+    --hash=sha256:8c497fff237d7b4e07e9ef1a640887fa4fb765647f86fbe00f969ff6280ce2bb \
+    --hash=sha256:8fdf95767f989b0cfedb85f7ed8ca215d4be728031f56ff5a519ee1e3276dc2e \
+    --hash=sha256:9bccbb3b40e3de10351f8f5068e105d0f4083b1a65fa07b6634fbc401a6287fd \
+    --hash=sha256:a0bcfe4d0d14aec44921545fd2af2338c7471de9cb701f1da4c9d85906ab847a \
+    --hash=sha256:a69525355a641bf8ef136a7fa447672fb54fe8d60cab5538d9eb7c6438543fb9 \
+    --hash=sha256:ada8121bcb4dac28d930febc791a69f7cb1673c8495e5eee274190b73a4559c1 \
+    --hash=sha256:bf97c10a3f5a7543f9b88cbf488d33d175e9146115a451ae34568597ba33dcde \
+    --hash=sha256:c22a2da7a198c28dd1a6e1136f19c830beab7fdca5b3e5c8bba8394f8a5c45b3 \
+    --hash=sha256:c2656924ec73e5939c76ac4c8b026fc203b83d8900362eb2599d8aee80e4880f \
+    --hash=sha256:c57b1b610bd1f40ba43970e11ce62821c2e6569e4d74023db19c6b26f246cb3b \
+    --hash=sha256:eddde82a035681427cbedded4e6eff5e57fa59216c2e3e90b10b19ab1d0a65c3 \
+    --hash=sha256:edec98c5e7c128328124a029bceb09eda2d526997780fef8d65e9a69eead963e \
+    --hash=sha256:ee787491dbfe082d9c3013f01f5991658b0f38aa8177e4cd4bf434c58f551702 \
+    --hash=sha256:f28dd15c6bb0b66ba09728cf09fd8736c304be29409bd8445a080c1280619e8c \
+    --hash=sha256:f984ca4b14914e6b4094c5d52a32ea16b49832c03bd17a110f004db3c223e8e1 \
+    --hash=sha256:fb65db5d7531bccf3a4f6bec3462223bea71384e2cda41da0f10b7c292b9e7c4 \
+    --hash=sha256:fe1c011a640a9f0791146011dfd3c7d9669785f9fed2b2a5f9e207536cf5c2fd
+    # via
+    #   pmdarima
+    #   pynndescent
+    #   shap
+    #   umap-learn
+scipy==1.17.1 \
+    --hash=sha256:010f4333c96c9bb1a4516269e33cb5917b08ef2166d5556ca2fd9f082a9e6ea0 \
+    --hash=sha256:02ae3b274fde71c5e92ac4d54bc06c42d80e399fec704383dcd99b301df37458 \
+    --hash=sha256:08b900519463543aa604a06bec02461558a6e1cef8fdbb8098f77a48a83c8118 \
+    --hash=sha256:131f5aaea57602008f9822e2115029b55d4b5f7c070287699fe45c661d051e39 \
+    --hash=sha256:158dd96d2207e21c966063e1635b1063cd7787b627b6f07305315dd73d9c679e \
+    --hash=sha256:1cc682cea2ae55524432f3cdff9e9a3be743d52a7443d0cba9017c23c87ae2f6 \
+    --hash=sha256:1f95b894f13729334fb990162e911c9e5dc1ab390c58aa6cbecb389c5b5e28ec \
+    --hash=sha256:200e1050faffacc162be6a486a984a0497866ec54149a01270adc8a59b7c7d21 \
+    --hash=sha256:2040ad4d1795a0ae89bfc7e8429677f365d45aa9fd5e4587cf1ea737f927b4a1 \
+    --hash=sha256:2b64ca7d4aee0102a97f3ba22124052b4bd2152522355073580bf4845e2550b6 \
+    --hash=sha256:2ceb2d3e01c5f1d83c4189737a42d9cb2fc38a6eeed225e7515eef71ad301dce \
+    --hash=sha256:35c3a56d2ef83efc372eaec584314bd0ef2e2f0d2adb21c55e6ad5b344c0dcb8 \
+    --hash=sha256:37425bc9175607b0268f493d79a292c39f9d001a357bebb6b88fdfaff13f6448 \
+    --hash=sha256:3877ac408e14da24a6196de0ddcace62092bfc12a83823e92e49e40747e52c19 \
+    --hash=sha256:3fd1fcdab3ea951b610dc4cef356d416d5802991e7e32b5254828d342f7b7e0b \
+    --hash=sha256:41b71f4a3a4cab9d366cd9065b288efc4d4f3c0b37a91a8e0947fb5bd7f31d87 \
+    --hash=sha256:43af8d1f3bea642559019edfe64e9b11192a8978efbd1539d7bc2aaa23d92de4 \
+    --hash=sha256:45abad819184f07240d8a696117a7aacd39787af9e0b719d00285549ed19a1e9 \
+    --hash=sha256:4b400bdc6f79fa02a4d86640310dde87a21fba0c979efff5248908c6f15fad1b \
+    --hash=sha256:4eb6c25dd62ee8d5edf68a8e1c171dd71c292fdae95d8aeb3dd7d7de4c364082 \
+    --hash=sha256:581b2264fc0aa555f3f435a5944da7504ea3a065d7029ad60e7c3d1ae09c5464 \
+    --hash=sha256:5cf36e801231b6a2059bf354720274b7558746f3b1a4efb43fcf557ccd484a87 \
+    --hash=sha256:5e3c5c011904115f88a39308379c17f91546f77c1667cea98739fe0fccea804c \
+    --hash=sha256:6609bc224e9568f65064cfa72edc0f24ee6655b47575954ec6339534b2798369 \
+    --hash=sha256:6e3dcd57ab780c741fde8dc68619de988b966db759a3c3152e8e9142c26295ad \
+    --hash=sha256:6fac755ca3d2c3edcb22f479fceaa241704111414831ddd3bc6056e18516892f \
+    --hash=sha256:744b2bf3640d907b79f3fd7874efe432d1cf171ee721243e350f55234b4cec4c \
+    --hash=sha256:74cbb80d93260fe2ffa334efa24cb8f2f0f622a9b9febf8b483c0b865bfb3475 \
+    --hash=sha256:766e0dc5a616d026a3a1cffa379af959671729083882f50307e18175797b3dfd \
+    --hash=sha256:7bdf2da170b67fdf10bca777614b1c7d96ae3ca5794fd9587dce41eb2966e866 \
+    --hash=sha256:7ff200bf9d24f2e4d5dc6ee8c3ac64d739d3a89e2326ba68aaf6c4a2b838fd7d \
+    --hash=sha256:844e165636711ef41f80b4103ed234181646b98a53c8f05da12ca5ca289134f6 \
+    --hash=sha256:8a604bae87c6195d8b1045eddece0514d041604b14f2727bbc2b3020172045eb \
+    --hash=sha256:94055a11dfebe37c656e70317e1996dc197e1a15bbcc351bcdd4610e128fe1ca \
+    --hash=sha256:95d8e012d8cb8816c226aef832200b1d45109ed4464303e997c5b13122b297c0 \
+    --hash=sha256:9cdc1a2fcfd5c52cfb3045feb399f7b3ce822abdde3a193a6b9a60b3cb5854ca \
+    --hash=sha256:9ecb4efb1cd6e8c4afea0daa91a87fbddbce1b99d2895d151596716c0b2e859d \
+    --hash=sha256:a3472cfbca0a54177d0faa68f697d8ba4c80bbdc19908c3465556d9f7efce9ee \
+    --hash=sha256:a4328d245944d09fd639771de275701ccadf5f781ba0ff092ad141e017eccda4 \
+    --hash=sha256:a48a72c77a310327f6a3a920092fa2b8fd03d7deaa60f093038f22d98e096717 \
+    --hash=sha256:a720477885a9d2411f94a93d16f9d89bad0f28ca23c3f8daa521e2dcc3f44d49 \
+    --hash=sha256:a77cbd07b940d326d39a1d1b37817e2ee4d79cb30e7338f3d0cddffae70fcaa2 \
+    --hash=sha256:a9956e4d4f4a301ebf6cde39850333a6b6110799d470dbbb1e25326ac447f52a \
+    --hash=sha256:adb2642e060a6549c343603a3851ba76ef0b74cc8c079a9a58121c7ec9fe2350 \
+    --hash=sha256:beeda3d4ae615106d7094f7e7cef6218392e4465cc95d25f900bebabfded0950 \
+    --hash=sha256:c80be5ede8f3f8eded4eff73cc99a25c388ce98e555b17d31da05287015ffa5b \
+    --hash=sha256:cc90d2e9c7e5c7f1a482c9875007c095c3194b1cfedca3c2f3291cdc2bc7c086 \
+    --hash=sha256:cd96a1898c0a47be4520327e01f874acfd61fb48a9420f8aa9f6483412ffa444 \
+    --hash=sha256:d2650c1fb97e184d12d8ba010493ee7b322864f7d3d00d3f9bb97d9c21de4068 \
+    --hash=sha256:d30e57c72013c2a4fe441c2fcb8e77b14e152ad48b5464858e07e2ad9fbfceff \
+    --hash=sha256:d59c30000a16d8edc7e64152e30220bfbd724c9bbb08368c054e24c651314f0a \
+    --hash=sha256:dbc12c9f3d185f5c737d801da555fb74b3dcfa1a50b66a1a93e09190f41fab50 \
+    --hash=sha256:e18f12c6b0bc5a592ed23d3f7b891f68fd7f8241d69b7883769eb5d5dfb52696 \
+    --hash=sha256:e19ebea31758fac5893a2ac360fedd00116cbb7628e650842a6691ba7ca28a21 \
+    --hash=sha256:e30bdeaa5deed6bc27b4cc490823cd0347d7dae09119b8803ae576ea0ce52e4c \
+    --hash=sha256:eb092099205ef62cd1782b006658db09e2fed75bffcae7cc0d44052d8aa0f484 \
+    --hash=sha256:eee2cfda04c00a857206a4330f0c5e3e56535494e30ca445eb19ec624ae75118 \
+    --hash=sha256:f4115102802df98b2b0db3cce5cb9b92572633a1197c77b7553e5203f284a5b3 \
+    --hash=sha256:f590cd684941912d10becc07325a3eeb77886fe981415660d9265c4c418d0bea \
+    --hash=sha256:f8885db0bc2bffa59d5c1b72fad7a6a92d3e80e7257f967dd81abb553a90d293 \
+    --hash=sha256:fcb310ddb270a06114bb64bbe53c94926b943f5b7f0842194d585c65eb4edd76
+    # via
+    #   lightgbm
+    #   pmdarima
+    #   pynndescent
+    #   scikit-learn
+    #   shap
+    #   statsmodels
+    #   umap-learn
+    #   xgboost
+setuptools==82.0.1 \
+    --hash=sha256:7d872682c5d01cfde07da7bccc7b65469d3dca203318515ada1de5eda35efbf9 \
+    --hash=sha256:a59e362652f08dcd477c78bb6e7bd9d80a7995bc73ce773050228a348ce2e5bb
+    # via pmdarima
+shap==0.51.0 \
+    --hash=sha256:07b0367408b1b9fc51556f2ddac5ee4209cc51be592099e6d51d0834c9b037d8 \
+    --hash=sha256:0b1f9e62d6a3fa28765d7b61abda7caf76aba21e769423fbf3ce8a7a5e498243 \
+    --hash=sha256:13eb21626ea671604769c847ac0604871a03df0842522087ffc00181683780a4 \
+    --hash=sha256:18828bc4f78adb644ae35c50e79a246d262fa6cf17143c78cca091796b21c27b \
+    --hash=sha256:1aa9f659d2028e26ac7ec34cafbc14585fdc14d0c8973e9442c65af1af1ff781 \
+    --hash=sha256:23c33eae29f887153ef952846ec3bff6abc0aed3aa01594e4ae66cd94a227a49 \
+    --hash=sha256:331d80a993e32404dd76254f5a82cb481453b4d9e58c0e7da13a3b700a381b03 \
+    --hash=sha256:33540a7e3c70bd1a742a4d0576c19b5e000165038de953d3ebf31a7bb53d01f4 \
+    --hash=sha256:3ddd314c9dc766f72027b3b6d9a8b975c7df67f1a27af7f857267c716b7d3dd8 \
+    --hash=sha256:4b4b81d7401bc821490148a694a9f149f8ef488fa973b49fdc8a7916a572750f \
+    --hash=sha256:5a909d6e306d4083e4862b6d097d53f3b4aa4d5cdf2ef4dbac5e8245160d9abd \
+    --hash=sha256:5f51ca55bda10b3fa2125f2b8e08e9d6a6edcbb0e752c67050e87a6d3ca7d53b \
+    --hash=sha256:6afaeac1fdd7883a058fb071c7044aff6c44699377a35a5d73e75b68564d0d47 \
+    --hash=sha256:6f3a83f28d2304f81645392a1d346154d9d992705e762fb949fa5371925399b2 \
+    --hash=sha256:71e18a6850af4cdeece1a3f9d4b633a421885fcfda079125e3d35ea08433d3eb \
+    --hash=sha256:724cdd8298450ae22b08ca40e07136c73e4e75dbdf8e3f07d741a291bf636dad \
+    --hash=sha256:80132eca5679e7e8da7a0d9bfee58d0a3979be25630fd6598ef608bbcefce784 \
+    --hash=sha256:86f24dab2c64d78f38170d490a03ff6fb1b48cf3bd0a1527e9bed23e74ad5d2c \
+    --hash=sha256:9b92f7371644c4a19660f734e0b0fe299d0eff273102230c9cf191e310576619 \
+    --hash=sha256:c3b878f6414213a12247faa00d609957fdfbcc33cfd48a6751500c4708b5666d \
+    --hash=sha256:c52aa8fb311502d5d25e8d631806326656318ab4094459ddbf1410837aaeb139 \
+    --hash=sha256:ca2a9171e6c5b9a700d585982d7fd8336856ad818e24264420c56f9d8f02a961 \
+    --hash=sha256:cfa17ff213657c9d50285aa923d79b0037a62e2ee1a31bc3eec7e196b00bdb59 \
+    --hash=sha256:d0c33498ed7042f7259ff207bd3aa1cc814fb759240e5f1500e018660b597c17 \
+    --hash=sha256:da930d73fa23d7a296660431f01726ae47ef2e7d9fee7e1632fb674be7b150b9 \
+    --hash=sha256:dee16e81082dec5ce2a37c41c2b9cbebcb4bf7de79133a72d84a4093b7d4158c \
+    --hash=sha256:e412bb475c9074ffd6684abb88d86d93275729b344cbfb37b4e4db37db759fbf \
+    --hash=sha256:ee76aa705927ac64acd4f506722f52596e77d3ced87078bc86bfcb4571c7b976 \
+    --hash=sha256:f32d006680708513efff07f67dcbe44a531b242ae042dee99b7024e210391ac2 \
+    --hash=sha256:f3efeef8a76e2ee735fad50f82e5a8e56ba8639f42e2fa50dc1997caed77c488 \
+    --hash=sha256:f461e5a1d6b0cae3fd9c6bd00c95111ed95b9e0020ec71f14291429ed17d49f4 \
+    --hash=sha256:ff5534e92f5876c74975b53cc6b251126bbe092e5032f81e1fe8583c4a74d58c
+    # via -r requirements.in
+six==1.17.0 \
+    --hash=sha256:4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274 \
+    --hash=sha256:ff70335d468e7eb6ec65b95b99d3a2836546063f63acc5171de367e834932a81
+    # via python-dateutil
+slicer==0.0.8 \
+    --hash=sha256:2e7553af73f0c0c2d355f4afcc3ecf97c6f2156fcf4593955c3f56cf6c4d6eb7 \
+    --hash=sha256:6c206258543aecd010d497dc2eca9d2805860a0b3758673903456b7df7934dc3
+    # via shap
+sqlalchemy==2.0.49 \
+    --hash=sha256:01146546d84185f12721a1d2ce0c6673451a7894d1460b592d378ca4871a0c72 \
+    --hash=sha256:059d7151fff513c53a4638da8778be7fce81a0c4854c7348ebd0c4078ddf28fe \
+    --hash=sha256:0c98c59075b890df8abfcc6ad632879540f5791c68baebacb4f833713b510e75 \
+    --hash=sha256:0f2fa354ba106eafff2c14b0cc51f22801d1e8b2e4149342023bd6f0955de5f5 \
+    --hash=sha256:12b04d1db2663b421fe072d638a138460a51d5a862403295671c4f3987fb9148 \
+    --hash=sha256:22d8798819f86720bc646ab015baff5ea4c971d68121cb36e2ebc2ee43ead2b7 \
+    --hash=sha256:233088b4b99ebcbc5258c755a097aa52fbf90727a03a5a80781c4b9c54347a2e \
+    --hash=sha256:24bd94bb301ec672d8f0623eba9226cc90d775d25a0c92b5f8e4965d7f3a1518 \
+    --hash=sha256:275424295f4256fd301744b8f335cff367825d270f155d522b30c7bf49903ee7 \
+    --hash=sha256:32fe6a41ad97302db2931f05bb91abbcc65b5ce4c675cd44b972428dd2947700 \
+    --hash=sha256:334edbcff10514ad1d66e3a70b339c0a29886394892490119dbb669627b17717 \
+    --hash=sha256:3bb9ec6436a820a4c006aad1ac351f12de2f2dbdaad171692ee457a02429b672 \
+    --hash=sha256:3ddcb27fb39171de36e207600116ac9dfd4ae46f86c82a9bf3934043e80ebb88 \
+    --hash=sha256:42e8804962f9e6f4be2cbaedc0c3718f08f60a16910fa3d86da5a1e3b1bfe60f \
+    --hash=sha256:43d044780732d9e0381ac8d5316f95d7f02ef04d6e4ef6dc82379f09795d993f \
+    --hash=sha256:46796877b47034b559a593d7e4b549aba151dae73f9e78212a3478161c12ab08 \
+    --hash=sha256:46d51518d53edfbe0563662c96954dc8fcace9832332b914375f45a99b77cc9a \
+    --hash=sha256:47604cb2159f8bbd5a1ab48a714557156320f20871ee64d550d8bf2683d980d3 \
+    --hash=sha256:4bbccb45260e4ff1b7db0be80a9025bb1e6698bdb808b83fff0000f7a90b2c0b \
+    --hash=sha256:4d4e5a0ceba319942fa6b585cf82539288a61e314ef006c1209f734551ab9536 \
+    --hash=sha256:55250fe61d6ebfd6934a272ee16ef1244e0f16b7af6cd18ab5b1fc9f08631db0 \
+    --hash=sha256:566df36fd0e901625523a5a1835032f1ebdd7f7886c54584143fa6c668b4df3b \
+    --hash=sha256:57ca426a48eb2c682dae8204cd89ea8ab7031e2675120a47924fabc7caacbc2a \
+    --hash=sha256:5e61abbec255be7b122aa461021daa7c3f310f3e743411a67079f9b3cc91ece3 \
+    --hash=sha256:618a308215b6cececb6240b9abde545e3acdabac7ae3e1d4e666896bf5ba44b4 \
+    --hash=sha256:62557958002b69699bdb7f5137c6714ca1133f045f97b3903964f47db97ea339 \
+    --hash=sha256:6270d717b11c5476b0cbb21eedc8d4dbb7d1a956fd6c15a23e96f197a6193158 \
+    --hash=sha256:685e93e9c8f399b0c96a624799820176312f5ceef958c0f88215af4013d29066 \
+    --hash=sha256:69469ce8ce7a8df4d37620e3163b71238719e1e2e5048d114a1b6ce0fbf8c662 \
+    --hash=sha256:6eb188b84269f357669b62cb576b5b918de10fb7c728a005fa0ebb0b758adce1 \
+    --hash=sha256:74ab4ee7794d7ed1b0c37e7333640e0f0a626fc7b398c07a7aef52f484fddde3 \
+    --hash=sha256:77641d299179c37b89cf2343ca9972c88bb6eef0d5fc504a2f86afd15cd5adf5 \
+    --hash=sha256:7c821c47ecfe05cc32140dcf8dc6fd5d21971c86dbd56eabfe5ba07a64910c01 \
+    --hash=sha256:7d6be30b2a75362325176c036d7fb8d19e8846c77e87683ffaa8177b35135613 \
+    --hash=sha256:7f605a456948c35260e7b2a39f8952a26f077fd25653c37740ed186b90aaa68a \
+    --hash=sha256:83101a6930332b87653886c01d1ee7e294b1fe46a07dd9a2d2b4f91bcc88eec0 \
+    --hash=sha256:88690f4e1f0fbf5339bedbb127e240fec1fd3070e9934c0b7bef83432f779d2f \
+    --hash=sha256:8a97ac839c2c6672c4865e48f3cbad7152cee85f4233fb4ca6291d775b9b954a \
+    --hash=sha256:8d6efc136f44a7e8bc8088507eaabbb8c2b55b3dbb63fe102c690da0ddebe55e \
+    --hash=sha256:8e20e511dc15265fb433571391ba313e10dd8ea7e509d51686a51313b4ac01a2 \
+    --hash=sha256:951d4a210744813be63019f3df343bf233b7432aadf0db54c75802247330d3af \
+    --hash=sha256:9ac7a3e245fd0310fd31495eb61af772e637bdf7d88ee81e7f10a3f271bff014 \
+    --hash=sha256:9b1c058c171b739e7c330760044803099c7fff11511e3ab3573e5327116a9c33 \
+    --hash=sha256:9c04bff9a5335eb95c6ecf1c117576a0aa560def274876fd156cfe5510fccc61 \
+    --hash=sha256:9c4969a86e41454f2858256c39bdfb966a20961e9b58bf8749b65abf447e9a8d \
+    --hash=sha256:9e0400fa22f79acc334d9a6b185dc00a44a8e6578aa7e12d0ddcd8434152b187 \
+    --hash=sha256:a05977bffe9bffd2229f477fa75eabe3192b1b05f408961d1bebff8d1cd4d401 \
+    --hash=sha256:a143af2ea6672f2af3f44ed8f9cd020e9cc34c56f0e8db12019d5d9ecf41cb3b \
+    --hash=sha256:a51d3db74ba489266ef55c7a4534eb0b8db9a326553df481c11e5d7660c8364d \
+    --hash=sha256:b95b2f470c1b2683febd2e7eab1d3f0e078c91dbdd0b00e9c645d07a413bb99f \
+    --hash=sha256:b9870d15ef00e4d0559ae10ee5bc71b654d1f20076dbe8bc7ed19b4c0625ceba \
+    --hash=sha256:c1dc3368794d522f43914e03312202523cc89692f5389c32bea0233924f8d977 \
+    --hash=sha256:c338ec6ec01c0bc8e735c58b9f5d51e75bacb6ff23296658826d7cfdfdb8678a \
+    --hash=sha256:c5070135e1b7409c4161133aa525419b0062088ed77c92b1da95366ec5cbebbe \
+    --hash=sha256:cc992c6ed024c8c3c592c5fc9846a03dd68a425674900c70122c77ea16c5fb0b \
+    --hash=sha256:d15950a57a210e36dd4cec1aac22787e2a4d57ba9318233e2ef8b2daf9ff2d5f \
+    --hash=sha256:d898cc2c76c135ef65517f4ddd7a3512fb41f23087b0650efb3418b8389a3cd1 \
+    --hash=sha256:d99945830a6f3e9638d89a28ed130b1eb24c91255e4f24366fbe699b983f29e4 \
+    --hash=sha256:da9b91bca419dc9b9267ffadde24eae9b1a6bffcd09d0a207e5e3af99a03ce0d \
+    --hash=sha256:df2d441bacf97022e81ad047e1597552eb3f83ca8a8f1a1fdd43cd7fe3898120 \
+    --hash=sha256:e06e617e3d4fd9e51d385dfe45b077a41e9d1b033a7702551e3278ac597dc750 \
+    --hash=sha256:ec44cfa7ef1a728e88ad41674de50f6db8cfdb3e2af84af86e0041aaf02d43d0 \
+    --hash=sha256:fb37f15714ec2652d574f021d479e78cd4eb9d04396dca36568fdfffb3487982
+    # via
+    #   alembic
+    #   optuna
+stanio==0.5.1 \
+    --hash=sha256:348d52f947dec431e118f4b601c4c5296929b86401d4d4dd5aa9373b0d4ae4ac \
+    --hash=sha256:99ad590daa5834681245c2b651716ec2e06223853661ada21430c621521c849f
+    # via cmdstanpy
+statsmodels==0.14.6 \
+    --hash=sha256:00781869991f8f02ad3610da6627fd26ebe262210287beb59761982a8fa88cae \
+    --hash=sha256:0444e88557df735eda7db330806fe09d51c9f888bb1f5906cb3a61fb1a3ed4a8 \
+    --hash=sha256:06eec42d682fdb09fe5d70a05930857efb141754ec5a5056a03304c1b5e32fd9 \
+    --hash=sha256:0f52ef0f0b63b8fd11e1ef1c2a1e73a410720b8715c9a83a26d733b6815597fe \
+    --hash=sha256:109012088b3e370080846ab053c76d125268631410142daad2f8c10770e8e8d9 \
+    --hash=sha256:151b73e29f01fe619dbce7f66d61a356e9d1fe5e906529b78807df9189c37721 \
+    --hash=sha256:19b58cf7474aa9e7e3b0771a66537148b2df9b5884fbf156096c0e6c1ff0469d \
+    --hash=sha256:26d4f0ed3b31f3c86f83a92f5c1f5cbe63fc992cd8915daf28ca49be14463a1c \
+    --hash=sha256:2738a00fca51196f5a7d44b06970ace6b8b30289839e4808d656f8a98e35faa7 \
+    --hash=sha256:3414e40c073d725007a6603a18247ab7af3467e1af4a5e5a24e4c27bc26673b4 \
+    --hash=sha256:341fa68a7403e10a95c7b6e41134b0da3a7b835ecff1eb266294408535a06eb6 \
+    --hash=sha256:3bef39f8587754f2d644b2e831e102fa08ace9a5a1af4b583b122e6fd3e083ab \
+    --hash=sha256:47ee7af083623d2091954fa71c7549b8443168f41b7c5dce66510274c50fd73e \
+    --hash=sha256:4d0c1b0f9f6915619e2a0d3853e5763d4d66876892ad352e7d7b93a737556978 \
+    --hash=sha256:4d17873d3e607d398b85126cd4ed7aad89e4e9d89fc744cdab1af3189a996c2a \
+    --hash=sha256:6ad5c2810fc6c684254a7792bf1cbaf1606cdee2a253f8bd259c43135d87cfb4 \
+    --hash=sha256:730f3297b26749b216a06e4327fe0be59b8d05f7d594fb6caff4287b69654589 \
+    --hash=sha256:73f305fbf31607b35ce919fae636ab8b80d175328ed38fdc6f354e813b86ee37 \
+    --hash=sha256:8021271a79f35b842c02a1794465a651a9d06ec2080f76ebc3b7adce77d08233 \
+    --hash=sha256:81e7dcc5e9587f2567e52deaff5220b175bf2f648951549eae5fc9383b62bc37 \
+    --hash=sha256:89ee7d595f5939cc20bf946faedcb5137d975f03ae080f300ebb4398f16a5bd4 \
+    --hash=sha256:9e0fc891d6358bf376cc0ae1fee10a650478172ae9ba359daba1785fc496cd1a \
+    --hash=sha256:9e8d2e519852adb1b420e018f5ac6e6684b2b877478adf7fda2cfdb58f5acb5d \
+    --hash=sha256:a3764ba8195c9baf0925a96da0743ff218067a269f01d155ca3558deed2658ca \
+    --hash=sha256:a518d3f9889ef920116f9fa56d0338069e110f823926356946dae83bc9e33e19 \
+    --hash=sha256:aa60d82e29fcd0a736e86feb63a11d2380322d77a9369a54be8b0965a3985f71 \
+    --hash=sha256:b328eafa86a2a67303fdb1d25677d15b70cd2a5229aabec7670ec5ea840f1375 \
+    --hash=sha256:b5eb07acd115aa6208b4058211138393a7e6c2cf12b6f213ede10f658f6a714f \
+    --hash=sha256:bdf1dfe2a3ca56f5529118baf33a13efed2783c528f4a36409b46bbd2d9d48eb \
+    --hash=sha256:d8c00a42863e4f4733ac9d078bbfad816249c01451740e6f5053ecc7db6d6368 \
+    --hash=sha256:e443e7077a6e2d3faeea72f5a92c9f12c63722686eb80bb40a0f04e4a7e267ad \
+    --hash=sha256:e83a9abe653835da3b37fb6ae04b45480c1de11b3134bd40b09717192a1456ea \
+    --hash=sha256:e93bd5d220f3cb6fc5fc1bffd5b094966cab8ee99f6c57c02e95710513d6ac3f \
+    --hash=sha256:f1c08befa85e93acc992b72a390ddb7bd876190f1360e61d10cf43833463bc9c \
+    --hash=sha256:f4ff0649a2df674c7ffb6fa1a06bffdb82a6adf09a48e90e000a15a6aaa734b0 \
+    --hash=sha256:fe76140ae7adc5ff0e60a3f0d56f4fffef484efa803c3efebf2fcd734d72ecb5
+    # via
+    #   -r requirements.in
+    #   pmdarima
+tenacity==9.1.4 \
+    --hash=sha256:6095a360c919085f28c6527de529e76a06ad89b23659fa881ae0649b867a9d55 \
+    --hash=sha256:adb31d4c263f2bd041081ab33b498309a57c77f9acf2db65aadf0898179cf93a
+    # via papermill
+text-unidecode==1.3 \
+    --hash=sha256:1311f10e8b895935241623731c2ba64f4c455287888b18189350b67134a822e8 \
+    --hash=sha256:bad6603bb14d279193107714b288be206cac565dfa49aa5b105294dd5c4aab93
+    # via python-slugify
+threadpoolctl==3.6.0 \
+    --hash=sha256:43a0b8fd5a2928500110039e43a5eed8480b918967083ea48dc3ab9f13c4a7fb \
+    --hash=sha256:8ab8b4aa3491d812b623328249fab5302a68d2d71745c8a4c719a2fcaba9f44e
+    # via scikit-learn
+tornado==6.5.5 \
+    --hash=sha256:192b8f3ea91bd7f1f50c06955416ed76c6b72f96779b962f07f911b91e8d30e9 \
+    --hash=sha256:2c9a876e094109333f888539ddb2de4361743e5d21eece20688e3e351e4990a6 \
+    --hash=sha256:36abed1754faeb80fbd6e64db2758091e1320f6bba74a4cf8c09cd18ccce8aca \
+    --hash=sha256:3f54aa540bdbfee7b9eb268ead60e7d199de5021facd276819c193c0fb28ea4e \
+    --hash=sha256:435319e9e340276428bbdb4e7fa732c2d399386d1de5686cb331ec8eee754f07 \
+    --hash=sha256:487dc9cc380e29f58c7ab88f9e27cdeef04b2140862e5076a66fb6bb68bb1bfa \
+    --hash=sha256:6443a794ba961a9f619b1ae926a2e900ac20c34483eea67be4ed8f1e58d3ef7b \
+    --hash=sha256:65a7f1d46d4bb41df1ac99f5fcb685fb25c7e61613742d5108b010975a9a6521 \
+    --hash=sha256:dd3eafaaeec1c7f2f8fdcd5f964e8907ad788fe8a5a32c4426fbbdda621223b7 \
+    --hash=sha256:e74c92e8e65086b338fd56333fb9a68b9f6f2fe7ad532645a290a464bcf46be5
+    # via jupyter-client
+tqdm==4.67.3 \
+    --hash=sha256:7d825f03f89244ef73f1d4ce193cb1774a8179fd96f31d7e1dcde62092b960bb \
+    --hash=sha256:ee1e4c0e59148062281c49d80b25b67771a127c85fc9676d3be5f243206826bf
+    # via
+    #   cmdstanpy
+    #   kaggle
+    #   optuna
+    #   papermill
+    #   prophet
+    #   shap
+    #   umap-learn
+traitlets==5.14.3 \
+    --hash=sha256:9ed0579d3502c94b4b3732ac120375cda96f923114522847de4b3bb98b96b6b7 \
+    --hash=sha256:b74e89e397b1ed28cc831db7aea759ba6640cb3de13090ca145426688ff1ac4f
+    # via
+    #   jupyter-client
+    #   jupyter-core
+    #   nbclient
+    #   nbformat
+typing-extensions==4.15.0 \
+    --hash=sha256:0cea48d173cc12fa28ecabc3b837ea3cf6f38c6d1136f85cbaaf598984861466 \
+    --hash=sha256:f0fa19c6845758ab08074a0cfa8b7aecb71c999ca73d62883bc25cc018c4e548
+    # via
+    #   alembic
+    #   shap
+    #   sqlalchemy
+umap-learn==0.5.12 \
+    --hash=sha256:6aff02ecac5f2aad9f3c65ee518d7ae93e1a985ae38721fdcffceee4232c33c7 \
+    --hash=sha256:f2a85d2a2adcb52b541bed9b27a23ca169b56bb1b23283abeebfb8dfb8a42fe5
+    # via -r requirements.in
+urllib3==2.6.3 \
+    --hash=sha256:1b62b6884944a57dbe321509ab94fd4d3b307075e0c2eae991ac71ee15ad38ed \
+    --hash=sha256:bf272323e553dfb2e87d9bfd225ca7b0f467b919d7bbd355436d3fd37cb0acd4
+    # via
+    #   kaggle
+    #   pmdarima
+    #   requests
+virtualenv==21.3.0 \
+    --hash=sha256:4d28ee41f6d9ec8f1f00cd472b9ffbcedda1b3d3b9a575b5c94a2d004fd51bd7 \
+    --hash=sha256:733750db978ec95c2d8eb4feadaa57091002bce404cb39ba69899cf7bd28944e
+    # via pre-commit
+webencodings==0.5.1 \
+    --hash=sha256:a0af1213f3c2226497a97e2b3aa01a7e4bee4f403f95be16fc9acd2947514a78 \
+    --hash=sha256:b36a1c245f2d304965eb4e0a82848379241dc04b865afcc4aab16748587e1923
+    # via bleach
+xgboost==3.2.0 \
+    --hash=sha256:0d169736fd836fc13646c7ab787167b3a8110351c2c6bc770c755ee1618f0442 \
+    --hash=sha256:2f661966d3e322536d9c448090a870fcba1e32ee5760c10b7c46bac7a342079a \
+    --hash=sha256:852eabc6d3b3702a59bf78dbfdcd1cb9c4d3a3b6e5ed1f8781d8b9512354fdd2 \
+    --hash=sha256:99b0e9a2a64896cdaf509c5e46372d336c692406646d20f2af505003c0c5d70d \
+    --hash=sha256:99b4a6bbcb47212fec5cf5fbe12347215f073c08967431b0122cfbd1ee70312c \
+    --hash=sha256:eabbd40d474b8dbf6cb3536325f9150b9e6f0db32d18de9914fb3227d0bef5b7
+    # via -r requirements.in
```

## Pre-flight Run Logs (Reference)

- Python 3.14 attempt: PASS — compile + install + import-smoke all green
- Python 3.13 attempt: SKIPPED (3.14 succeeded; auto-fallback did not fire)

Full pre-flight logs preserved in `/tmp/preflight-22/run-*.log` during the planning session; not committed to source control. The decision and final state are captured in `22-SUMMARY.md`.

---
*Audit produced by plan 22-03 from artifacts staged by plan 22-02.*
