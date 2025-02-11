#global candidate rc0
%if 0%{?rhel}
%bcond_with toolsonly
%else
%bcond_without toolsonly
%endif

Name:     uboot-tools
Version:  2025.01
Release:  3%{?candidate:.%{candidate}}%{?dist}
Epoch:    1
Summary:  U-Boot utilities
# Automatically converted from old format: GPLv2+ BSD LGPL-2.1+ LGPL-2.0+ - review is highly recommended.
License:  GPL-2.0-or-later AND LicenseRef-Callaway-BSD AND LGPL-2.1-or-later AND LGPL-2.0-or-later
URL:      http://www.denx.de/wiki/U-Boot
ExcludeArch: s390x
Source0:  https://ftp.denx.de/pub/u-boot/u-boot-%{version}%{?candidate:-%{candidate}}.tar.bz2
Source1:  aarch64-boards

# This is now legacy, most devices use bootflow, we keep this for the laggards
Patch1:   uefi-distro-load-FDT-from-any-partition-on-boot-device.patch
# Identify VFAT partitions as ESP, allows EFI setvar on our images
Patch2:   uefi-Add-all-options-for-EFI-System-Partitions.patch
# New function to find fdt for loading from disk
Patch3:   uefi-initial-find_fdt_location-for-finding-the-DT-on-disk.patch
# Fedora patches to enable/disable features
Patch4:   disable-VBE-by-default.patch
Patch5:   enable-bootmenu-by-default.patch
# Should be upstream but it's taking time
#Patch6:   Add-video-damage-tracking.patch

# Device improvments
# RPi
Patch10:  rpi-Add-identifiers-for-the-new-RPi-5-series.patch
# Rockchips improvements
Patch11:  rockchip-Enable-preboot-start-for-pci-usb.patch
#Patch12:  rockchip-Modernise-Geekbox-config.patch

BuildRequires:  bc
BuildRequires:  bison
BuildRequires:  dtc
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  gnutls-devel
BuildRequires:  libuuid-devel
BuildRequires:  make
BuildRequires:  ncurses-devel
BuildRequires:  openssl-devel
BuildRequires:  openssl-devel-engine
BuildRequires:  perl-interpreter
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-libfdt
BuildRequires:  SDL2-devel
BuildRequires:  swig
%if %{with toolsonly}
%ifarch aarch64
BuildRequires:  arm-trusted-firmware-armv8
BuildRequires:  crust-firmware
BuildRequires:  python3-pyelftools
BuildRequires:  xxd
%endif
%endif
Requires:       dtc

%description
This package contains a few U-Boot utilities - mkimage for creating boot images
and fw_printenv/fw_setenv for manipulating the boot environment variables.

%if %{with toolsonly}
%ifarch aarch64
%package     -n uboot-images-armv8
Summary:     U-Boot firmware images for aarch64 boards
BuildArch:   noarch

%description -n uboot-images-armv8
U-Boot firmware binaries for aarch64 boards
%endif
%endif

%prep
%autosetup -p1 -n u-boot-%{version}%{?candidate:-%{candidate}}

cp %SOURCE1 .

%build
mkdir builds

%make_build HOSTCC="gcc $RPM_OPT_FLAGS" CROSS_COMPILE="" tools-only_defconfig O=builds/
%make_build HOSTCC="gcc $RPM_OPT_FLAGS" CROSS_COMPILE="" tools-all O=builds/

%if %{with toolsonly}
%ifarch aarch64
for board in $(cat %{_arch}-boards)
do
  echo "Building board: $board"
  mkdir builds/$(echo $board)/

  # ATF selection, needs improving, suggestions of ATF SoC to Board matrix welcome
  sun50i=(a64-olinuxino a64-olinuxino-emmc amarula_a64_relic bananapi_m64 nanopi_a64 oceanic_5205_5inmfd orangepi_win pine64-lts pine64_plus pine64_plus pinebook pinephone pinephone pinetab sopine_baseboard teres_i)
  if [[ " ${sun50i[*]} " == *" $board "* ]]; then
    echo "Board: $board using sun50i_a64"
    cp /usr/share/arm-trusted-firmware/sun50i_a64/bl31.bin builds/$(echo $board)/atf-bl31
    cp /usr/share/crust-firmware/a64/scp.bin builds/$(echo $board)/
  fi
  sun50h5=(bananapi_m2_plus_h5 emlid_neutis_n5_devboard libretech_all_h3_cc_h5 libretech_all_h3_it_h5 libretech_all_h5_cc_h5 nanopi_neo2 nanopi_neo_plus2 nanopi_r1s_h5 orangepi_pc2 orangepi_prime orangepi_zero_plus2 orangepi_zero_plus)
  if [[ " ${sun50h5[*]} " == *" $board "* ]]; then
    echo "Board: $board using sun50i_h6"
    cp /usr/share/arm-trusted-firmware/sun50i_a64/bl31.bin builds/$(echo $board)/atf-bl31
    cp /usr/share/crust-firmware/h5/scp.bin builds/$(echo $board)/
  fi
  sun50h6=(beelink_gs1 emlid_neutis_n5_devboard orangepi_3 orangepi_lite2 orangepi_one_plus pine_h64 tanix_tx6)
  if [[ " ${sun50h6[*]} " == *" $board "* ]]; then
    echo "Board: $board using sun50i_h6"
    cp /usr/share/arm-trusted-firmware/sun50i_h6/bl31.bin builds/$(echo $board)/atf-bl31
    cp /usr/share/crust-firmware/h6/scp.bin builds/$(echo $board)/
  fi
  sun50i_h616=(orangepi_zero2 orangepi_zero2w orangepi_zero3 transpeed-8k618-t x96_mate)
  if [[ " ${sun50i_h616[*]} " == *" $board "* ]]; then
    echo "Board: $board using sun50i_h616"
    cp /usr/share/arm-trusted-firmware/sun50i_h616/bl31.bin builds/$(echo $board)/atf-bl31
  fi
  rk3328=(evb-rk3328 nanopi-r2c-plus-rk3328 nanopi-r2c-rk3328 nanopi-r2s-rk3328 nanopi-r2s-plus-rk3328 orangepi-r1-plus-lts-rk3328 orangepi-r1-plus-rk3328 roc-cc-rk3328 rock64-rk3328 rock-pi-e-rk3328 rock-pi-e-v3-rk3328)
  if [[ " ${rk3328[*]} " == *" $board "* ]]; then
    echo "Board: $board using rk3328"
    cp /usr/share/arm-trusted-firmware/rk3328/bl31.elf builds/$(echo $board)/atf-bl31
  fi
  rk3368=(evb-px5 geekbox)
  if [[ " ${rk3368[*]} " == *" $board "* ]]; then
    echo "Board: $board using rk3368"
    cp /usr/share/arm-trusted-firmware/rk3368/bl31.elf builds/$(echo $board)/atf-bl31
  fi
  rk3399=(eaidk-610-rk3399 evb-rk3399 ficus-rk3399 firefly-rk3399 khadas-edge-captain-rk3399 khadas-edge-rk3399 khadas-edge-v-rk3399 leez-rk3399 nanopc-t4-rk3399 nanopi-m4-2gb-rk3399 nanopi-m4b-rk3399 nanopi-m4-rk3399 nanopi-neo4-rk3399 nanopi-r4s-rk3399 orangepi-rk3399 pinebook-pro-rk3399 pinephone-pro-rk3399 puma-rk3399 rock-4c-plus-rk3399 rock-4se-rk3399 rock960-rk3399 rock-pi-4c-rk3399 rock-pi-4-rk3399 rock-pi-n10-rk3399pro rockpro64-rk3399 roc-pc-mezzanine-rk3399 roc-pc-rk3399)
  if [[ " ${rk3399[*]} " == *" $board "* ]]; then
    echo "Board: $board using rk3399"
    cp /usr/share/arm-trusted-firmware/rk3399/* builds/$(echo $board)/
    cp builds/$(echo $board)/bl31.elf builds/$(echo $board)/atf-bl31
  fi
  # End ATF

  make $(echo $board)_defconfig O=builds/$(echo $board)/
  BL31=builds/$(echo $board)/atf-bl31 %make_build HOSTCC="gcc $RPM_OPT_FLAGS" CROSS_COMPILE="" O=builds/$(echo $board)/

done

%endif
%endif

%install
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_mandir}/man1
mkdir -p %{buildroot}%{_datadir}/uboot/

%if %{with toolsonly}
%ifarch aarch64
for board in $(ls builds)
do
 for file in u-boot.bin u-boot.img u-boot-dtb.img u-boot-sunxi-with-spl.bin u-boot-rockchip-spi.bin u-boot-rockchip.bin
 do
  if [ -f builds/$(echo $board)/$(echo $file) ]; then
    install -pD -m 0644 builds/$(echo $board)/$(echo $file) %{buildroot}%{_datadir}/uboot/$(echo $board)/$(echo $file)
  fi
 done
done

# Just for xilinx_zynqmp_virt
install -pD -m 0644 builds/xilinx_zynqmp_virt/u-boot.itb %{buildroot}%{_datadir}/uboot/xilinx_zynqmp_virt/u-boot.itb
install -pD -m 0644 builds/xilinx_zynqmp_virt/spl/boot.bin %{buildroot}%{_datadir}/uboot/xilinx_zynqmp_virt/boot.bin

# For Apple M-series we also need the nodtb variant
install -pD -m 0644 builds/apple_m1/u-boot-nodtb.bin %{buildroot}%{_datadir}/uboot/apple_m1/u-boot-nodtb.bin

# Bit of a hack to remove binaries we don't use as they're large
for board in $(ls builds)
do
  rm -f %{buildroot}%{_datadir}/uboot/$(echo $board)/u-boot.dtb
  if [ -f %{buildroot}%{_datadir}/uboot/$(echo $board)/u-boot-sunxi-with-spl.bin ]; then
    rm -f %{buildroot}%{_datadir}/uboot/$(echo $board)/u-boot{,-dtb}.*
    rm -f %{buildroot}%{_datadir}/uboot/$(echo $board)/sunxi-spl.bin
  fi
  if [ -f %{buildroot}%{_datadir}/uboot/$(echo $board)/idbloader.img ]; then
    rm -f %{buildroot}%{_datadir}/uboot/$(echo $board)/u-boot.bin
    rm -f %{buildroot}%{_datadir}/uboot/$(echo $board)/u-boot{,-dtb}.img
  fi
done
%endif
%endif

for tool in dumpimage env/fw_printenv fdt_add_pubkey fit_check_sign fit_info gdb/gdbcont gdb/gdbsend gen_eth_addr gen_ethaddr_crc ifwitool img2srec kwboot mkeficapsule mkenvimage mkimage mksunxiboot ncb proftool sunxi-spl-image-builder
do
install -p -m 0755 builds/tools/$tool %{buildroot}%{_bindir}
done
for tool in dumpimage kwboot mkeficapsule mkimage
do
install -p -m 0644 doc/$tool.1 %{buildroot}%{_mandir}/man1
done

install -p -m 0755 builds/tools/env/fw_printenv %{buildroot}%{_bindir}
( cd %{buildroot}%{_bindir}; ln -sf fw_printenv fw_setenv )

%files
%license Licenses/*
%doc README doc/develop/distro.rst doc/README.gpt
%doc doc/develop/uefi doc/usage doc/arch/arm64.rst
%{_bindir}/*
%{_mandir}/man1/dumpimage.1*
%{_mandir}/man1/kwboot.1*
%{_mandir}/man1/mkeficapsule.1*
%{_mandir}/man1/mkimage.1*

%if %{with toolsonly}
%ifarch aarch64
%files -n uboot-images-armv8
%license Licenses/*
%dir %{_datadir}/uboot/
%{_datadir}/uboot/*
%endif
%endif

%changelog
* Tue Jan 28 2025 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2025.01-3
- Add new fdt_add_pubkey tool

* Sun Jan 19 2025 Fedora Release Engineering <releng@fedoraproject.org> - 1:2025.01-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Tue Jan 07 2025 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2025.01-1
- Update to 2025.01 GA

* Mon Jan 06 2025 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2025.01-0.2.rc6
- Rebuild for TF-A 2.12

* Tue Dec 31 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2025.01-0.1.rc6
- Update to 2025.01 RC6

* Fri Oct 11 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.10-1
- Update to 2024.10 GA
- Fix passing RPi firmware CMA setting to kernel DT
- Update Geekbox

* Thu Oct 03 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.10-0.8.rc6
- Pass CMA FW setting through to kernel DT for Raspberry Pi

* Tue Oct 01 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.10-0.7.rc6
- Update to 2024.10 RC6

* Mon Sep 16 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.10-0.6.rc5
- Update to 2024.10 RC5

* Fri Sep  6 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.10-0.5.rc4
- Add missing licenses directory

* Tue Sep 03 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.10-0.4.rc4
- Update to 2024.10 RC4

* Mon Sep 02 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.10-0.3.rc3
- Fix Allwinner firmware chainloading (rhbz#2309138)
- Fix ATF firmware selection on a number of devices
- Support Allwinner SCP firmware (fixes suspend/resume)

* Tue Aug 27 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.10-0.2.rc3
- Update to 2024.10 RC3
- Enable initial QCM6490 SoC support

* Thu Aug 15 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.10-0.1.rc2
- Update to 2024.10 RC2

* Tue Jul 23 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.07-1
- Update to 2024.07

* Sat Jul 20 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1:2024.07-0.3.rc4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Tue Jun 18 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.07-0.2.rc4
- Update to 2024.07 RC4

* Sat May 25 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.07-0.1.rc3
- Update to 2024.07 RC3

* Wed Apr 03 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.04-1
- Update to 2024.04 GA
- Rockchip rk3328 USB fixes

* Wed Mar 27 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.04-0.8.rc5
- Update to 2024.04 RC5

* Thu Mar 21 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.04-0.7.rc4
- Updated patch for DTB loading

* Fri Mar 15 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.04-0.6.rc4
- Updated fix for FDT load

* Wed Mar 13 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.04-0.5.rc4
- Fixes for Rockchip rk3399 autoboot

* Tue Mar 12 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.04-0.4.rc4
- Update to 2024.04 RC4
- Initial fix for loading DT off /boot (rhbz 2247873)

* Thu Feb 29 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.04-0.3.rc3
- Update to 2024.04 RC3
- Enable a number of new upstream devices
- Upstream now builds Rockchip SPI artifacts
- Various cleanups
- Fix ESP partition detection to enable EFI vars

* Wed Feb 14 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.04-0.2.rc2
- Update to 2024.04 RC2

* Sat Jan 27 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1:2024.01-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Mon Jan 08 2024 Peter Robinson <pbrobinson@fedoraproject.org> - 1:2024.01-1
- Update to 2024.01
