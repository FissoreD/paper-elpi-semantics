FNAME=main

TEX_CMD = pdflatex -synctex=1 -interaction=nonstopmode --shell-escape 
GENERATOR = python3 extract_code.py

all: tex_code aux
	echo '{"security":{"enable_cwd_config": true}}' > ~/.latexminted_config && \
	$(MAKE) main

TEXFILES := $(shell find src -type f -name '*.tex')
PDFFILES := $(TEXFILES:.tex=.pdf)
MINFILES := $(shell find elpi-formalization -type f -name '*.v')
IGNFILES := $(MINFILES:.v=.ign)

aux: $(PDFFILES)
tex_code: $(IGNFILES)

%.pdf: %.tex
	cd $(dir $<) && $(TEX_CMD) $(notdir $<) && $(TEX_CMD) $(notdir $<)

%.ign: %.v
	$(GENERATOR) $<

main:
	${TEX_CMD} ${FNAME}.tex && \
	bibtex ${FNAME}.aux && \
	${TEX_CMD} ${FNAME}.tex && \
	${TEX_CMD} ${FNAME}.tex

update_submodule:
	git submodule update --remote

docker:
	#docker create --name latex dfissore/latex2025:latest
	docker cp ./ latex:/data/ && docker ps -a && \
	docker start -i latex && docker cp latex:/data/main.pdf . && \
	docker cp latex:/data/main.synctex.gz . && \
	docker cp latex:/data/main.log . && \
	docker cp latex:/data/main.blg . && \
	docker cp latex:/data/main.bbl . && \
	docker cp latex:/data/main.aux . && \
	docker cp latex:/data/main.out . && \
	mkdir -p pdf && cp main.pdf pdf

ci:
	$(MAKE) update_submodule && \
	docker create --name latex dfissore/latex2025:latest && \
	docker cp ./ latex:/data/ && docker ps -a && \
	docker start -i latex && docker cp latex:/data/main.pdf . && \
	mkdir -p pdf && mv main.pdf pdf
	cd elpi-formalization && git archive --format=zip --prefix=code-paper-89/ -o ../artefact.zip HEAD
	mv artefact.zip pdf