OALISTURL:=ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/file_list.txt

open-access.txt:
	wget $(OALISTURL) -O $@.tmp
	mv $@.tmp $@
