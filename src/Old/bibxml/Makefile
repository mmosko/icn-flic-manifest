.PHONY: all

RFCS= reference.RFC.2119.xml reference.RFC.2629.xml reference.RFC.3532.xml reference.RFC.3552.xml \
	  reference.RFC.5226.xml reference.RFC.8569.xml reference.RFC.8609.xml

IDS= reference.I-D.irtf-icnrg-terminology.xml

all: $(RFCS) $(IDS)

clean: 
	rm -f $(RFCS) $(IDS)

$(RFCS):
	wget http://xml2rfc.tools.ietf.org/public/rfc/bibxml/$@

$(IDS):
	wget http://xml2rfc.tools.ietf.org/public/rfc/bibxml-ids/$@

