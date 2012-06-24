Summary:	A cron-like program that can run jobs lost during downtime
Summary(pl):	Wersja crona z mo�liwo�ci� uruchamiania zapomnianych proces�w
Summary(pt_BR):	Auxiliar do cron para m�quinas que n�o ficam ligadas o tempo todo
Name:		anacron
Version:	2.3
Release:	22
License:	GPL
Group:		Daemons
Source0:	http://dl.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
# Source0-md5:	865cc1dfe1ed75c470d3e6de13763f03
Source1:	%{name}tab
Source2:	%{name}.init
Patch0:		%{name}-SIGTERM.patch
Patch1:		%{name}-sendmail.patch
URL:		http://anacron.sourceforge.net/
Requires:	/usr/lib/sendmail
Provides:	crondaemon
Prereq:		/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Anacron (like `anac(h)ronistic') is a periodic command scheduler. It
executes commands at intervals specified in days. Unlike cron, it does
not assume that the system is running continuously. It can therefore
be used to control the execution of daily, weekly and monthly jobs (or
anything with a period of n days), on systems that don't run 24 hours
a day. When installed and configured properly, Anacron will make sure
that the commands are run at the specified intervals as closely as
machine-uptime permits.

This package is pre-configured to execute the daily jobs of the PLD
Linux system. You should install this program if your system isn't
powered on 24 hours a day to make sure the maintenance jobs of other
Red Hat Linux packages are executed each day.

%description -l pl
Anacron (od ,,anac(h)ronistic'') zajmuje si� okresowym wykonywaniem
polece�. Wykonuje je w odst�pach b�d�cych wielokrotno�ci� dni. W
przeciwie�stwie do crona nie zak�ada, �e system dzia�a 24 godziny na
dob�. Dzi�ki temu mo�e by� u�ywany do wykonywania codziennych,
cotygodniowych i comiesi�cznych (lub innych powtarzaj�cych si� co ile�
dni) zada� w systemach, kt�re nie s� w��czone non-stop. Zainstalowany
i poprawnie skonfigurowany Anacron zapewni wykonywanie zleconych zada�
tak blisko wyznaczonych termin�w, jak tylko mo�liwe.

Ten pakiet zosta� wst�pnie skonfigurowany do dzia�ania w systemie PLD
Linux. Powiniene� zainstalowa� ten program na systemach, kt�re nie s�
w��czone non-stop aby zapewni� uruchamianie r�nych zada�
utrzymuj�cych system we w�a�ciwych odst�pach czasu.

%description -l pt_BR
Anacron � uma agenda para marcar a execu��o de comandos em hor�rios
programados. Ao contr�rio do cron, o anacron n�o requer que o sistema
esteja rodando continuamente, podendo ser executado em sistemas que
n�o est�o ligados 24 horas por dia.

%prep
%setup -q
%patch0 -p1
%patch1 -p1

%build
%{__make} CFLAGS="%{rpmcflags}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir},%{_sbindir},%{_mandir}/man{5,8}} \
	$RPM_BUILD_ROOT/{var/spool/anacron,etc/rc.d/init.d}

install anacron $RPM_BUILD_ROOT%{_sbindir}
install anacron.8 $RPM_BUILD_ROOT%{_mandir}/man8/
install anacrontab.5 $RPM_BUILD_ROOT%{_mandir}/man5/
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

for i in cron.daily cron.weekly cron.monthly; do
install  -d $RPM_BUILD_ROOT%{_sysconfdir}/$i/
cat << EOF > $RPM_BUILD_ROOT%{_sysconfdir}/$i/0anacron
#!/bin/sh
#
# anacron's cron script
#
# This script updates anacron time stamps. It is called through run-parts
# either by anacron itself or by cron.
#
# The script is called "0anacron" to assure that it will be executed
# _before_ all other scripts.

anacron -u $i

EOF
done

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add anacron

if [ -f /var/lock/subsys/anacron ]; then
	/etc/rc.d/init.d/anacron restart >&2
else
	echo "Run \"/etc/rc.d/init.d/anacron start\" to start Anacron daemon."
fi

%preun
if [ "$1" = "0" ];then
	if [ -f /var/lock/subsys/anacron ]; then
		/etc/rc.d/init.d/anacron stop >&2
	fi
	/sbin/chkconfig --del anacron
fi

%files
%defattr(644,root,root,755)
%doc ChangeLog README TODO
%attr(755,root,root) %{_sbindir}/anacron
%attr(754,root,root) /etc/rc.d/init.d/*
%config %{_sysconfdir}/anacrontab
%dir /var/spool/anacron/
%config %{_sysconfdir}/cron.daily/0anacron
%config %{_sysconfdir}/cron.monthly/0anacron
%config %{_sysconfdir}/cron.weekly/0anacron
%{_mandir}/man[58]/*
