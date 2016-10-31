clean:
	rm *.aux *.log *.tex *.pdf

all: record empty test bad

record:
	./caml-tex.py test_record.mlt
	pdflatex -shell-escape test_record.mlt.tex
	pdflatex -shell-escape test_record.mlt.tex
	open test_record.mlt.pdf

empty:
	./caml-tex.py test_empty.mlt
	pdflatex -shell-escape test_empty.mlt.tex
	pdflatex -shell-escape test_empty.mlt.tex
	open test_empty.mlt.pdf

test:
	./caml-tex.py test.mlt
	pdflatex -shell-escape test.mlt.tex
	pdflatex -shell-escape test.mlt.tex
	open test.mlt.pdf

bad:
	./caml-tex.py test_bad.mlt
	pdflatex -shell-escape test_bad.mlt.tex
	pdflatex -shell-escape test_bad.mlt.tex
	open test_bad.mlt.pdf
