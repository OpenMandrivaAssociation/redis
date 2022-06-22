#define beta rc1

Name:		redis
Version:	7.0.0
Release:	2
Summary:	A persistent key-value database
Group:		Databases
License:	BSD
URL:		http://redis.io/
Patch0:		http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/0001-1st-man-pageis-for-redis-cli-redis-benchmark-redis-c.patch
Patch2:		redis-4.0.8-workaround-make-deadlock.patch
Patch5:		redis-4.0.5-openmandriva-redis.conf.patch
Source0:	http://download.redis.io/releases/%{name}-%{version}%{?beta:-%{beta}}.tar.gz
Source1:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis-limit-systemd
Source2:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis-sentinel.service
Source3:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis-shutdown
Source4:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis.logrotate
# Based on, but not identical to, Fedora's file
Source5:	redis.service
Source6:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis.tmpfiles
Source7:	redis.sysusers
BuildRequires:	pkgconfig(lua)
BuildRequires:	procps-ng
BuildRequires:	systemd-rpm-macros
BuildRequires:	pkgconfig(libsystemd)
BuildRequires:	tcl
BuildRequires:	atomic-devel
Requires:	/bin/awk
Requires:	logrotate
Requires(pre):	systemd
%systemd_requires

%description
Redis is an advanced key-value store.
It is similar to memcached but the data set is not volatile,
and values can be strings, exactly like in memcached,
but also lists, sets, and ordered sets.
All this data types can be manipulated with atomic operations
to push/pop elements, add/remove elements, perform server side
union, intersection, difference between sets, and so
forth. Redis supports different kind of sorting abilities.

%prep
%autosetup -p1 -n %{name}-%{version}%{?beta:-%{beta}}

rm -rf deps/jemalloc

# No hidden build.
sed -i -e 's|\t@|\t|g' deps/lua/src/Makefile
sed -i -e 's|$(QUIET_CC)||g' src/Makefile
sed -i -e 's|$(QUIET_LINK)||g' src/Makefile
sed -i -e 's|$(QUIET_INSTALL)||g' src/Makefile
# Ensure deps are built with proper flags
sed -i -e 's|$(CFLAGS)|%{optflags}|g' deps/Makefile
sed -i -e 's|OPTIMIZATION?=-O3|OPTIMIZATION=%{optflags}|g' deps/hiredis/Makefile
sed -i -e 's|$(LDFLAGS)|%{build_ldflags}|g' deps/hiredis/Makefile
sed -i -e 's|$(CFLAGS)|%{optflags}|g' deps/linenoise/Makefile
sed -i -e 's|$(LDFLAGS)|%{build_ldflags}|g' deps/linenoise/Makefile

%build
%ifarch %{ix86}
# Workaround for a crash while building with
# clang 7.0.0-0.333395
export CC=gcc
export CXX=g++
export LD=gcc
echo 'CC=gcc' >temp
cat src/Makefile >>temp
mv -f temp src/Makefile
%endif
%make_build \
	DEBUG="" \
	LDFLAGS="%{build_ldflags}" \
	CFLAGS+="%{optflags}" \
	LUA_LDFLAGS+="%{build_ldflags}" \
	MALLOC=libc \
	all

%install
%make install INSTALL="install -p" PREFIX=%{buildroot}%{_prefix}

# Filesystem
mkdir -p %{buildroot}%{_sharedstatedir}/%{name} \
	%{buildroot}%{_localstatedir}/log/%{name} \
	%{buildroot}%{_localstatedir}/run/%{name}

# Extras
install -pDm 755 %{S:3} %{buildroot}%{_bindir}/%{name}-shutdown

# Logrotate file
install -pDm 644 %{S:4} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Configuration files
install -pDm 644 redis.conf %{buildroot}%{_sysconfdir}/redis.conf
install -pDm 644 sentinel.conf %{buildroot}%{_sysconfdir}/redis-sentinel.conf

# Systemd unit files
install -pDm 644 %{S:2} %{buildroot}%{_unitdir}/redis-sentinel.service
install -pDm 644 %{S:5} %{buildroot}%{_unitdir}/redis.service

# tmpfiles setup
install -pDm 644 %{S:6} %{buildroot}%{_tmpfilesdir}/%{name}.conf

# Systemd limits
install -pDm 644 %{S:1} %{buildroot}%{_sysconfdir}/systemd/system/%{name}.service.d/limit.conf
install -pDm 644 %{S:1} %{buildroot}%{_sysconfdir}/systemd/system/%{name}-sentinel.service.d/limit.conf

install -Dpm 644 %{SOURCE7} %{buildroot}%{_sysusersdir}/%{name}.conf

%check
# Currently says all tests passed and then segfaults
#make test

%pre
%sysusers_create_package %{name} %{SOURCE7}

%files
%doc 00-RELEASENOTES BUGS COPYING
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}-sentinel.conf
%dir %attr(0755, redis, root) %{_localstatedir}/lib/%{name}
%dir %attr(0755, redis, root) %{_localstatedir}/log/%{name}
%{_bindir}/%{name}-*
%{_sysusersdir}/%{name}.conf
%{_tmpfilesdir}/%{name}.conf
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-sentinel.service
%dir %{_sysconfdir}/systemd/system/%{name}.service.d
%{_sysconfdir}/systemd/system/%{name}.service.d/limit.conf
%dir %{_sysconfdir}/systemd/system/%{name}-sentinel.service.d
%{_sysconfdir}/systemd/system/%{name}-sentinel.service.d/limit.conf
