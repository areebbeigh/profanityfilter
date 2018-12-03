make_doc_files() {
    cd docs
    rm -r build/html
    make html
}

# push_github_pages() {
#     cd ../github-pages
#     git config --global user.email "travis@travis-ci.org"
#     git config --global user.name "Travis CI"

#     git add ./*
#     git commit --message "[ci skip] Travis build: $TRAVIS_BUILD_NUMBER"

#     git remote remove origin
#     git remote add origin https://${GH_TOKEN}@github.com/areebbeigh/profanityfilter.git

#     git push origin gh-pages
# }

pip install sphinx
make_doc_files

# push_github_pages
