main:
	$(MAKE) tex_code && \
	pdflatex -synctex=1 -interaction=nonstopmode --shell-escape main.tex

gen = python3 extract_code.py $(1);

tex_code:
	$(foreach F, $(wildcard ./elpi-formalization/theories/*.v), $(call gen,$(F))) true

ci:
	git submodule update --remote && \
	docker create --name latex dfissore/latex2023:latest && \
	docker cp ./ latex:/data/ && docker ps -a && \
	docker start -i latex && docker cp latex:/data/main.pdf . && \
	mkdir -p pdf && mv main.pdf pdf 

.PHONY: tex_code