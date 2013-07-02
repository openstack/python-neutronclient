_neutron_opts="" # lazy init
_neutron_flags="" # lazy init
_neutron_opts_exp="" # lazy init
_neutron()
{
	local cur prev nbc cflags
	COMPREPLY=()
	cur="${COMP_WORDS[COMP_CWORD]}"
	prev="${COMP_WORDS[COMP_CWORD-1]}"

	if [ "x$_neutron_opts" == "x" ] ; then
		nbc="`neutron bash-completion`"
		_neutron_opts="`echo "$nbc" | sed -e "s/--[a-z0-9_-]*//g" -e "s/\s\s*/ /g"`"
		_neutron_flags="`echo " $nbc" | sed -e "s/ [^-][^-][a-z0-9_-]*//g" -e "s/\s\s*/ /g"`"
		_neutron_opts_exp="`echo "$_neutron_opts" | sed -e "s/\s/|/g"`"
	fi

	if [[ " ${COMP_WORDS[@]} " =~ " "($_neutron_opts_exp)" " && "$prev" != "help" ]] ; then
		COMPLETION_CACHE=~/.neutronclient/*/*-cache
		cflags="$_neutron_flags "$(cat $COMPLETION_CACHE 2> /dev/null | tr '\n' ' ')
		COMPREPLY=($(compgen -W "${cflags}" -- ${cur}))
	else
		COMPREPLY=($(compgen -W "${_neutron_opts}" -- ${cur}))
	fi
	return 0
}
complete -F _neutron neutron
