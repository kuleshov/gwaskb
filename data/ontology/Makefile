EFOURL:=http://data.bioontology.org/ontologies/EFO/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb&download_format=csv

efo.csv:
	wget "$(EFOURL)" -O $@.gz
	gunzip $@.gz
