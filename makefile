clean:
	rm *.aux *.log *.tex *.pdf

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
