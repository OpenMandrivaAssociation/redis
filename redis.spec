Name:		redis
Version:	4.0.8
Release:	1
Summary:	A persistent key-value database
Group:		Databases
License:	BSD
URL:		http://redis.io/
Patch0:		http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/0001-1st-man-pageis-for-redis-cli-redis-benchmark-redis-c.patch
Patch1:		http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/0002-install-redis-check-rdb-as-a-symlink-instead-of-dupl.patch
Patch2:		redis-4.0.8-workaround-make-deadlock.patch
Patch5:		redis-4.0.5-openmandriva-redis.conf.patch
Source0:	http://download.redis.io/releases/%{name}-%{version}.tar.gz
Source1:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis-limit-systemd
Source2:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis-sentinel.service
Source3:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis-shutdown
Source4:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis.logrotate
# Based on, but not identical to, Fedora's file
Source5:	redis.service
Source6:	http://pkgs.fedoraproject.org/cgit/rpms/redis.git/plain/redis.tmpfiles
BuildRequires:	pkgconfig(lua)
BuildRequires:	procps-ng
BuildRequires:	systemd
BuildRequires:	tcl
Requires:	/bin/awk
Requires:	logrotate
Requires(pre):	rpm-helper >= 0.24.8-1
Requires(postun):rpm-helper >= 0.24.8-1

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
%setup -q
%apply_patches

rm -rf deps/jemalloc

# No hidden build.
sed -i -e 's|\t@|\t|g' deps/lua/src/Makefile
sed -i -e 's|$(QUIET_CC)||g' src/Makefile
sed -i -e 's|$(QUIET_LINK)||g' src/Makefile
sed -i -e 's|$(QUIET_INSTALL)||g' src/Makefile
# Ensure deps are built with proper flags
sed -i -e 's|$(CFLAGS)|%{optflags}|g' deps/Makefile
sed -i -e 's|OPTIMIZATION?=-O3|OPTIMIZATION=%{optflags}|g' deps/hiredis/Makefile
sed -i -e 's|$(LDFLAGS)|%{?__global_ldflags}|g' deps/hiredis/Makefile
sed -i -e 's|$(CFLAGS)|%{optflags}|g' deps/linenoise/Makefile
sed -i -e 's|$(LDFLAGS)|%{?__global_ldflags}|g' deps/linenoise/Makefile


%build
%make \
	DEBUG="" \
	LDFLAGS="%{ldflags}" \
	CFLAGS+="%{optflags}" \
	LUA_LDFLAGS+="%{ldflags}" \
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

%check
# Currently says all tests passed and then segfaults
#make test

%pre
%_pre_useradd %{name}  %{_sharedstatedir}/%{name} /sbin/nologin

%postun 
%_postun_userdel %{name}

%files
%doc 00-RELEASENOTES BUGS COPYING
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}-sentinel.conf
%dir %attr(0755, redis, root) %{_localstatedir}/lib/%{name}
%dir %attr(0755, redis, root) %{_localstatedir}/log/%{name}
%{_bindir}/%{name}-*
%{_tmpfilesdir}/%{name}.conf
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-sentinel.service
%dir %{_sysconfdir}/systemd/system/%{name}.service.d
%{_sysconfdir}/systemd/system/%{name}.service.d/limit.conf
%dir %{_sysconfdir}/systemd/system/%{name}-sentinel.service.d
%{_sysconfdir}/systemd/system/%{name}-sentinel.service.d/limit.conf
