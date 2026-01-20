FNAME=main

TEX_CMD = pdflatex -synctex=1 -interaction=nonstopmode --shell-escape ${FNAME}.tex

main:
	$(MAKE) tex_code && \
	${TEX_CMD} && \
	bibtex ${TEX_CMD} && \
	${TEX_CMD}

gen = python3 extract_code.py $(1);

tex_code:
	$(foreach F, $(wildcard ./elpi-formalization/theories/*.v), $(call gen,$(F))) true

update_submodule:
	git submodule update --remote

ci:
	$(MAKE) update_submodule && \
	docker create --name latex dfissore/latex2023:latest && \
	docker cp ./ latex:/data/ && docker ps -a && \
	docker start -i latex && docker cp latex:/data/main.pdf . && \
	mkdir -p pdf && mv main.pdf pdf 

.PHONY: tex_code