main:
	pdflatex main.tex

ci:
	docker create --name latex dfissore/latex2023:latest && \
	docker cp ./ latex:/data/ && docker ps -a && \
	docker start -i latex && docker cp latex:/data/main.pdf . && \
	mkdir -p pdf && mv main.pdf pdf 