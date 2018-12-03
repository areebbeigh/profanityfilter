make_doc_files() {
    cd docs
    rm -r build/html
    make html
}

pip install sphinx
make_doc_files
