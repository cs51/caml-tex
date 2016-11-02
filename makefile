ctex:
	./run -o pset2.tex pset2.mlt

pset:
	pdflatex -shell-escape pset2.tex
	pdflatex -shell-escape pset2.tex

