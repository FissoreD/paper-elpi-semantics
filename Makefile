FNAME=main

TEX_CMD = pdflatex -synctex=1 -interaction=nonstopmode --shell-escape 

all:
	echo '{"security":{"enable_cwd_config": true}}' > ~/.latexminted_config && \
	$(MAKE) all_aux && \
	$(MAKE) tex_code && \
	$(MAKE) main

main:
	${TEX_CMD} ${FNAME}.tex && \
	bibtex ${FNAME}.aux && \
	${TEX_CMD} ${FNAME}.tex && \
	${TEX_CMD} ${FNAME}.tex

gen = python3 extract_code.py $(1);

build_tree:
	cd ./src/exec_example1 && \
	for f in $$(ls *.tex); do \
		$(TEX_CMD) $$f; \
	done

build_elpi:
	cd ./src/exec_example1E && \
	for f in $$(ls *.tex); do \
		$(TEX_CMD) $$f; \
	done

build_aux:
	cd ./src && \
	for f in $$(ls *.tex); do \
		$(TEX_CMD) $$f; \
	done


tex_code:
	$(foreach F, $(wildcard ./elpi-formalization/theories/*.v), $(call gen,$(F))) true

update_submodule:
	git submodule update --remote

all_aux:
	$(MAKE) build_tree && \
	$(MAKE) build_aux && \
	$(MAKE) build_elpi

ci:
	$(MAKE) update_submodule && \
	docker create --name latex dfissore/latex2025:latest && \
	docker cp ./ latex:/data/ && docker ps -a && \
	docker start -i latex && docker cp latex:/data/main.pdf . && \
	mkdir -p pdf && mv main.pdf pdf 

.PHONY: tex_code