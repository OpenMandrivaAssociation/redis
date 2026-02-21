#define beta rc1

Name:		redis
Version:	8.6.0
Release:	2
Summary:	A persistent key-value database
Group:		Databases
License:	BSD
URL:		https://redis.io/
# Also https://github.com/redis/redis/
Patch0:		http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/0001-1st-man-pageis-for-redis-cli-redis-benchmark-redis-c.patch
Patch2:		redis-4.0.8-workaround-make-deadlock.patch
Patch5:		redis-4.0.5-openmandriva-redis.conf.patch
Source0:	http://download.redis.io/releases/%{name}-%{version}%{?beta:-%{beta}}.tar.gz
Source1:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis-limit-systemd
Source2:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis-sentinel.service
Source3:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis-shutdown
Source4:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis.logrotate
Source5:	redis@.service
Source6:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis.tmpfiles
Source7:	redis.sysusers
BuildRequires:	make
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

%package sentinel
Summary:	Tool for monitoring multiple redis instances and handling failover
Group:		Servers
# Only because %{_bindir}/redis-sentinel is a symlink to %{_bindir}/redis-server
# They should actually be on separate hosts if possible
Requires:	%{name} = %{EVRD}

%description sentinel
Tool for monitoring multiple redis instances and handling failover

%package benchmark
Summary:	Tool for measuring the performance of redis
Group:		Servers

%description benchmark
Tool for measuring the performance of redis

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
# ifarch below intentionally says x86_64 and not %{x86_64},
# znver1 is not affected by the problem it works around
# (build time error caused by _Float32 at -Os)
%make_build \
	DEBUG="" \
	LDFLAGS="%{build_ldflags}" \
%ifarch x86_64
	CFLAGS+="%{optflags} -O2" \
%else
	CFLAGS+="%{optflags}" \
%endif
	LUA_LDFLAGS+="%{build_ldflags}" \
	MALLOC=libc \
	all

%install
%make_install INSTALL="install -p" PREFIX=%{buildroot}%{_prefix}

# Filesystem
mkdir -p %{buildroot}%{_sharedstatedir}/%{name} \
	%{buildroot}%{_localstatedir}/log/%{name} \
	%{buildroot}%{_localstatedir}/run/%{name} \
	%{buildroot}%{_localstatedir}/lib/%{name}

# Extras
install -pDm 755 %{S:3} %{buildroot}%{_bindir}/%{name}-shutdown

# Logrotate file
install -pDm 644 %{S:4} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Configuration files
install -pDm 644 redis.conf %{buildroot}%{_sysconfdir}/redis/example.conf
install -pDm 644 sentinel.conf %{buildroot}%{_sysconfdir}/redis/redis-sentinel.conf

# Systemd unit files
install -pDm 644 %{S:2} %{buildroot}%{_unitdir}/redis-sentinel.service
install -pDm 644 %{S:5} %{buildroot}%{_unitdir}/redis@.service

# tmpfiles setup
install -pDm 644 %{S:6} %{buildroot}%{_tmpfilesdir}/%{name}.conf

# Systemd limits
install -pDm 644 %{S:1} %{buildroot}%{_sysconfdir}/systemd/system/%{name}.service.d/limit.conf
install -pDm 644 %{S:1} %{buildroot}%{_sysconfdir}/systemd/system/%{name}-sentinel.service.d/limit.conf

install -Dpm 644 %{S:7} %{buildroot}%{_sysusersdir}/%{name}.conf

mkdir -p %{buildroot}/srv/%{name}

# We don't need this anymore -- systemd handles shutdown
rm %{buildroot}%{_bindir}/redis-shutdown

#check
# The test suite needs exactly tcl 8.5 -- won't work with 9.x
# make test

# /var/lib/redis moved to /srv/redis 2026-02-21 after 6.0, 8.6.0-2
%pretrans -p <lua>
omv = require("omv")
omv.dir2Symlink("/var/lib/redis", "/srv/redis")

%files
%doc 00-RELEASENOTES BUGS
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%dir %{_sysconfdir}/redis
%{_sysconfdir}/redis/example.conf
%ghost %{_localstatedir}/lib/%{name}
%dir %attr(0755, redis, root) /srv/%{name}
%dir %attr(0755, redis, root) %{_localstatedir}/log/%{name}
%{_bindir}/%{name}-cli
%{_bindir}/%{name}-server
%{_bindir}/%{name}-check-aof
%{_bindir}/%{name}-check-rdb
%{_sysusersdir}/%{name}.conf
%{_tmpfilesdir}/%{name}.conf
%{_unitdir}/%{name}@.service
%dir %{_sysconfdir}/systemd/system/%{name}.service.d
%{_sysconfdir}/systemd/system/%{name}.service.d/limit.conf

%files benchmark
%{_bindir}/%{name}-benchmark

%files sentinel
%{_bindir}/%{name}-sentinel
%{_unitdir}/%{name}-sentinel.service
%config(noreplace) %{_sysconfdir}/redis/%{name}-sentinel.conf
%dir %{_sysconfdir}/systemd/system/%{name}-sentinel.service.d
%{_sysconfdir}/systemd/system/%{name}-sentinel.service.d/limit.conf
