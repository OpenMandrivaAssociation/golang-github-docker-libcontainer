%if 0%{?fedora} || 0%{?rhel} == 6
%global with_devel 1
%global with_bundled 0
%global with_debug 1
# some tests are failing
%global with_check 0
%global with_unit_test 1
%else
%global with_devel 0
%global with_bundled 1
%global with_debug 0
%global with_check 0
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%if ! 0%{?gobuild:1}
%define gobuild(o:) go build -ldflags "${LDFLAGS:-} -B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \\n')" -a -v -x %{?**};
%endif

%global provider        github
%global provider_tld    com
%global project         docker
%global repo            libcontainer
# https://github.com/docker/libcontainer
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          c9643688cb73c2588a9c9b14357bda6c3a9df67f
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           golang-github-docker-libcontainer
Version:        2.1.1
Release:        0.14.git%{shortcommit}%{?dist}
Summary:        Configuration options for containers
License:        ASL 2.0
URL:            https://%{provider_prefix}
Source0:	https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz
Patch0:         update-to-newer-signature-of-systemd.Conn-methods.patch
Patch1:         libcontainer-fixDup3syscall.patch

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 %{arm}}
# Include ppc64le once updated to newer version
ExcludeArch: ppc64 ppc64le
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%if ! 0%{?with_bundled}
BuildRequires: golang(github.com/Sirupsen/logrus)
BuildRequires: golang(github.com/codegangsta/cli) >= 1.1.0-1
BuildRequires: golang(github.com/coreos/go-systemd/dbus)
BuildRequires: golang(github.com/docker/go-units)
BuildRequires: golang(github.com/docker/docker/pkg/mount)
BuildRequires: golang(github.com/docker/docker/pkg/symlink)
BuildRequires: golang(github.com/docker/docker/pkg/term)
BuildRequires: golang(github.com/godbus/dbus)
BuildRequires: golang(github.com/golang/protobuf/proto)
BuildRequires: golang(github.com/syndtr/gocapability/capability) >= 0-0.9
%endif

Provides:       nsinit = %{version}-%{release}

%description
libcontainer specifies configuration options for what a container is. It
provides a native Go implementation for using Linux namespaces with no
external dependencies. libcontainer provides many convenience functions for
working with namespaces, networking, and management. 

This package provides the nsinit binary as well, but it is currently for
debugging purposes only and not officially supported.

%if 0%{?with_devel}
%package devel
Summary:        Configuration options for containers
BuildArch:      noarch

%if 0%{?with_check}
BuildRequires: golang(github.com/Sirupsen/logrus)
BuildRequires: golang(github.com/coreos/go-systemd/dbus)
BuildRequires: golang(github.com/docker/docker/pkg/mount)
BuildRequires: golang(github.com/docker/docker/pkg/symlink)
BuildRequires: golang(github.com/godbus/dbus)
BuildRequires: golang(github.com/golang/protobuf/proto)
BuildRequires: golang(github.com/syndtr/gocapability/capability) >= 0-0.9
%endif

Requires: golang(github.com/Sirupsen/logrus)
Requires: golang(github.com/coreos/go-systemd/dbus)
Requires: golang(github.com/docker/docker/pkg/mount)
Requires: golang(github.com/docker/docker/pkg/symlink)
Requires: golang(github.com/godbus/dbus)
Requires: golang(github.com/golang/protobuf/proto)
Requires: golang(github.com/syndtr/gocapability/capability) >= 0-0.9

Provides: golang(%{import_path}) = %{version}-%{release}
Provides: golang(%{import_path}/apparmor) = %{version}-%{release}
Provides: golang(%{import_path}/cgroups) = %{version}-%{release}
Provides: golang(%{import_path}/cgroups/fs) = %{version}-%{release}
Provides: golang(%{import_path}/cgroups/systemd) = %{version}-%{release}
Provides: golang(%{import_path}/configs) = %{version}-%{release}
Provides: golang(%{import_path}/configs/validate) = %{version}-%{release}
Provides: golang(%{import_path}/criurpc) = %{version}-%{release}
Provides: golang(%{import_path}/devices) = %{version}-%{release}
Provides: golang(%{import_path}/integration) = %{version}-%{release}
Provides: golang(%{import_path}/label) = %{version}-%{release}
Provides: golang(%{import_path}/netlink) = %{version}-%{release}
Provides: golang(%{import_path}/nsenter) = %{version}-%{release}
Provides: golang(%{import_path}/selinux) = %{version}-%{release}
Provides: golang(%{import_path}/stacktrace) = %{version}-%{release}
Provides: golang(%{import_path}/system) = %{version}-%{release}
Provides: golang(%{import_path}/user) = %{version}-%{release}
Provides: golang(%{import_path}/utils) = %{version}-%{release}
Provides: golang(%{import_path}/xattr) = %{version}-%{release}

%description devel
libcontainer specifies configuration options for what a container is. It
provides a native Go implementation for using Linux namespaces with no
external dependencies. libcontainer provides many convenience functions for
working with namespaces, networking, and management. 

This package contains library source intended for building other packages
which use libcontainer.
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%package unit-test-devel
Summary:         Unit tests for %{name} package
%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:        %{name}-devel = %{version}-%{release}

%if 0%{?with_check} && ! 0%{?with_bundled}
%endif

%description unit-test-devel
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{commit}
%if ! 0%{?with_bundled}
%patch0 -p1
%patch1 -p1 -b .dup3
%endif

%build
mkdir -p src/github.com/docker
ln -s ../../../ src/github.com/docker/libcontainer

%if ! 0%{?with_bundled}
export GOPATH=$(pwd):%{gopath}
%else
export GOPATH=$(pwd):$(pwd)/vendor:%{gopath}
%endif

%gobuild -o bin/nsinit %{import_path}/nsinit

%install
# Install nsinit
install -d %{buildroot}%{_bindir}
install -p -m 755 bin/nsinit %{buildroot}%{_bindir}/nsinit

# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
echo "%%dir %%{gopath}/src/%%{import_path}/." >> devel.file-list
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go" | egrep -v "./vendor/src") ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test} && 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test-devel.file-list
for file in $(find . -iname "*_test.go" | egrep -v "./vendor/src") ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test-devel.file-list
done
%endif

%if 0%{?with_devel}
sort -u -o devel.file-list devel.file-list
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%if ! 0%{?with_bundled}
export GOPATH=%{buildroot}/%{gopath}:%{gopath}
%else
export GOPATH=%{buildroot}/%{gopath}:$(pwd)/vendor:%{gopath}
%endif

%if ! 0%{?gotest:1}
%global gotest go test
%endif

%gotest %{import_path}
%gotest %{import_path}/cgroups
%gotest %{import_path}/cgroups/fs
%gotest %{import_path}/configs
%gotest %{import_path}/devices
%gotest %{import_path}/integration
%gotest %{import_path}/label
%gotest %{import_path}/netlink
%gotest %{import_path}/nsenter
%gotest %{import_path}/selinux
%gotest %{import_path}/stacktrace
%gotest %{import_path}/user
%gotest %{import_path}/utils
%gotest %{import_path}/xattr
%endif

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE
%doc MAINTAINERS MAINTAINERS_GUIDE.md NOTICE
%doc PRINCIPLES.md README.md ROADMAP.md
%{_bindir}/nsinit

%if 0%{?with_devel}
%files devel -f devel.file-list
%license LICENSE
%doc ROADMAP.md PRINCIPLES.md MAINTAINERS_GUIDE.md CONTRIBUTING.md README.md SPEC.md
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%files unit-test-devel -f unit-test-devel.file-list
%license LICENSE
%doc ROADMAP.md PRINCIPLES.md MAINTAINERS_GUIDE.md CONTRIBUTING.md README.md SPEC.md
%endif

%changelog
* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.1-0.14.gitc964368
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.1-0.13.gitc964368
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.1-0.12.gitc964368
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 03 2017 Jan Chaloupka <jchaloup@redhat.com> - 2.1.1-0.11.gitc964368
- Exclude ppc64le (the package needs to be pdated to newer version)
  related: #1164989

* Tue Jun 27 2017 Jan Chaloupka <jchaloup@redhat.com> - 2.1.1-0.10.gitc964368
- Exclude ppc64 arch (missing docker)
  related: #1164989

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.1-0.9.gitc964368
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.1-0.8.gitc964368
- https://fedoraproject.org/wiki/Changes/golang1.7

* Sat Apr  9 2016 Peter Robinson <pbrobinson@fedoraproject.org> 2.1.1-0.7.gitc964368
- Fix builds on aarch64

* Thu Mar 17 2016 jchaloup <jchaloup@redhat.com> - 2.1.1-0.6.gitc964368
- Polish spec file
- Patch systemd.Conn methods
  resolves: #1230658

* Mon Feb 22 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.1-0.5.gitc964368
- https://fedoraproject.org/wiki/Changes/golang1.6

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.1.1-0.4.gitc964368
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.1.1-0.3.gitc964368
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sun Jun 14 2015 jchaloup <jchaloup@redhat.com> - 2.1.1-0.2.gitc964368
- Don't remove _build directory, it is used during debuginfo extracting
  At the same time don't include _build directory in devel subpackage.
  resolves: #1231486

* Thu Jun 11 2015 jchaloup <jchaloup@redhat.com> - 2.1.1-0.1.gitc964368
- Update to 2.1.1
  Ppolish spec file
  Use license macro for LICENSE
  Remove runtime dependency on golang
  resolves: #1230658

* Mon Apr 20 2015 jchaloup <jchaloup@redhat.com> - 1.4.0-3.gitbada39c
- Bump to upstream bada39cf31c3305810c2575e036f594a7dc3c98f
  related: #1164989

* Tue Mar 31 2015 jchaloup <jchaloup@redhat.com> - 1.4.0-2.gitd7dea0e
- Add [B]R to devel subpackage
  related: #1164989

* Mon Mar 09 2015 jchaloup <jchaloup@redhat.com> - 1.4.0-1.git83663f8
- Bump to upstream 83663f82e3d76f57ea57faf80b8fd7eb96933b9b
  related: #1164989

* Tue Nov 18 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-3.git28cb5f9
- Resolves: rhbz#1164989 - update to atleast b9c834b7

* Mon Oct 20 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-2.gitc907e40
- install namespaces/nsenter

* Mon Oct 20 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.2.0-1.gitc907e40
- bump to v1.2.0 commit c907e406fe81320d87b58edf74953ceb08facc13

* Sat Aug 23 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.0-10.git
- Include syncpipe, system and user dirs missed in previous build

* Fri Aug 22 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.0-9.git
- Update to db65c35051d05f3fb218a0e84a11267e0894fe0a for docker 1.2.0

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1.0-8.git29363e2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 15 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.0-7.git
- Resolves: rhbz#1130500
- update to upstream commit 29363e2d2d7b8f62a5f353be333758f83df540a9

* Thu Jul 31 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.0-6
- Resolves: rhbz#1111916 - package review request
- remove attr for fedora
- correct NVR for codegangsta/cli 1.1.0-1

* Wed Jul 30 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.0-5
- LICENSE file installed in main package
- defattr gotten rid of

* Wed Jul 30 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.0-4
- Update BRs for main package

* Mon Jul 28 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.0-3
- nsinit needs docker-io-pkg-devel to build

* Fri Jul 25 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> - 1.1.0-2
- nsinit description: debugging only and no official support

* Fri Jul 25 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> 1.1.0-1
- use v1.1.0
- do not own dirs owned by golang
- do not redefine macros defined in golang
- main package provides nsinit

* Sat Jun 21 2014 Lokesh Mandvekar <lsm5@fedoraproject.org> 1.0.1-1
- Initial fedora package
