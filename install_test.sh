mkdir -p .installs

git clone --depth=1 https://github.com/facebookresearch/torchbeast.git .installs/torchbeast
cd .installs/torchbeast/nest
CXX=c++ pip install . -vv
cd ../../..
