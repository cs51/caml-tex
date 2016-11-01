clean:
	rm *.aux *.log *.tex *.pdf *.pyc
	rm testfiles/*.tex testfiles/*.log, testfiles/*.aux

all: record empty test bad

mlt:
	./run testfiles/test.mlt -o testfiles/test.mlt.tex

record:
	./run testfiles/test_record.mlt -o testfiles/test_record.mlt.tex
	pdflatex -shell-escape -output-directory=testfiles testfiles/test_record.mlt.tex 

empty:
	./run testfiles/test_empty.mlt -o testfiles/test_empty.mlt.tex
	pdflatex -shell-escape -output-directory=testfiles testfiles/test_empty.mlt.tex 
	pdflatex -shell-escape -output-directory=testfiles testfiles/test_empty.mlt.tex 
	open testfiles/test_empty.mlt.pdf

test:
	./run testfiles/test.mlt -o testfiles/test.mlt.tex
	pdflatex -shell-escape -output-directory=testfiles testfiles/test.mlt.tex 
	pdflatex -shell-escape -output-directory=testfiles testfiles/test.mlt.tex 
	open testfiles/test.mlt.pdf

bad:
	./run testfiles/test_bad.mlt -o testfiles/test_bad.mlt.tex
	pdflatex -shell-escape -output-directory=testfiles testfiles/test_bad.mlt.tex 
	pdflatex -shell-escape -output-directory=testfiles testfiles/test_bad.mlt.tex 
	open testfiles/test_bad.mlt.pdf
