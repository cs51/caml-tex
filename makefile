clean:
	rm *.aux *.log *.tex *.pdf

record:
	./caml-tex.py test_record.mlt
	pdflatex -shell-escape test_record.mlt.tex
	pdflatex -shell-escape test_record.mlt.tex
	open test_record.mlt.pdf