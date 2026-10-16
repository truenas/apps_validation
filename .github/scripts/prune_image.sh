#!/bin/bash
# Runs inside a container of the built image. Removes the parts of the TrueNAS rootfs (the middleware
# base image) that rendering and validating apps never use. Deleting files only shrinks the image once
# it is flattened, the build workflow does that with `docker export | docker import`.
#
# Sizes as measured on middleware:master (2026-10), ~6.7 GB in total.
# Kept on purpose: python packages and the system libraries behind them (importing middleware pulls in
# its whole API), git, dpkg state, the docker CLI (the renderer talks to the host's docker socket).
set -euo pipefail

PRUNE=(
  /usr/share/middlewared/docs                       # 2.0 GB  API docs (api-docs pulls them from middleware:master)
  /usr/lib/modules                                  # 1.7 GB  kernel modules, containers use the host kernel
  /usr/share/truenas/sysext-extensions              # 451 MB  systemd system extensions
  /usr/share/AAVMF                                  # 385 MB  arm64 VM firmware
  /usr/lib/firmware                                 # 343 MB  hardware firmware
  /usr/libexec/netdata                              # 328 MB  netdata (reporting)
  /boot                                             # 168 MB  kernel and initramfs
  /usr/share/locale                                 # 131 MB  translations
  /usr/lib/x86_64-linux-gnu/libLLVM.so.*            # 124 MB  LLVM, only used by bpftrace/perf/bcc and GPU drivers
  /usr/bin/dockerd                                  # 108 MB  docker daemon, the host's daemon is used through the socket
  /usr/share/truenas/webui                          # 106 MB  web UI
  /var/cache/apt                                    # 103 MB  downloaded .deb files
  /usr/bin/rclone                                   #  97 MB  cloud sync
  /var/lib/apt/lists                                #  92 MB  apt package lists, `apt-get update` recreates them
  /usr/src/linux-headers-truenas-debug-amd64        #  72 MB  kernel headers
  /usr/src/linux-headers-truenas-production-amd64   #  72 MB  kernel headers
  /usr/lib/x86_64-linux-gnu/libclang-cpp.so.*       #  68 MB  clang, only used by bcc
  /usr/share/netdata                                #  55 MB  netdata (reporting)
  /usr/bin/containerd                               #  43 MB  container runtime
  /usr/lib/x86_64-linux-gnu/libgallium-*.so         #  41 MB  mesa GPU drivers
  /usr/lib/x86_64-linux-gnu/libclang-*.so.*         #  37 MB  clang, only used by bpftrace/bcc
  /usr/share/man                                    #  37 MB  man pages
  /usr/bin/qemu-system-aarch64                      #  33 MB  VM emulators
  /usr/bin/qemu-system-arm                          #  30 MB  VM emulators
  /usr/bin/qemu-system-i386                         #  28 MB  VM emulators
  /usr/bin/qemu-system-x86_64                       #  28 MB  VM emulators
  /usr/bin/qemu-system-x86_64-microvm               #   8 MB  VM emulators
  /usr/lib/x86_64-linux-gnu/libz3.so.*              #  27 MB  z3 solver, only used by LLVM
  /usr/bin/ctr                                      #  26 MB  containerd CLI
  /usr/share/OVMF                                   #  17 MB  x86 VM firmware
  /usr/share/doc                                    #  14 MB  package docs
  /usr/share/qemu                                   #  12 MB  VM firmware
  /usr/bin/containerd-shim-runc-v2                  #   8 MB  container runtime
  /usr/share/ovmf                                   #   4 MB  x86 VM firmware
  /usr/share/qemu-efi-aarch64                       #   3 MB  arm64 VM firmware
)

rm -rf "${PRUNE[@]}"
# apt expects the directory to exist
mkdir -p /var/lib/apt/lists/partial
