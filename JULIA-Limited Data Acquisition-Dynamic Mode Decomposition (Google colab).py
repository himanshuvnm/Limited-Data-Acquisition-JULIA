# -*- coding: utf-8 -*-
"""Copy of Julia_Colab_Notebook_Template.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1BdsnCY1CQxOnQX49gYBt529ZizeyDe9f

# <img src="https://github.com/JuliaLang/julia-logo-graphics/raw/master/images/julia-logo-color.png" height="100" /> _Colab Notebook Template_

## Instructions
1. Work on a copy of this notebook: _File_ > _Save a copy in Drive_ (you will need a Google account). Alternatively, you can download the notebook using _File_ > _Download .ipynb_, then upload it to [Colab](https://colab.research.google.com/).
2. If you need a GPU: _Runtime_ > _Change runtime type_ > _Harware accelerator_ = _GPU_.
3. Execute the following cell (click on it and press Ctrl+Enter) to install Julia, IJulia and other packages (if needed, update `JULIA_VERSION` and the other parameters). This takes a couple of minutes.
4. Reload this page (press Ctrl+R, or ⌘+R, or the F5 key) and continue to the next section.

_Notes_:
* If your Colab Runtime gets reset (e.g., due to inactivity), repeat steps 2, 3 and 4.
* After installation, if you want to change the Julia version or activate/deactivate the GPU, you will need to reset the Runtime: _Runtime_ > _Factory reset runtime_ and repeat steps 3 and 4.
"""

# Commented out IPython magic to ensure Python compatibility.
# %%shell
# set -e
# 
# #---------------------------------------------------#
# JULIA_VERSION="1.8.2" # any version ≥ 0.7.0
# JULIA_PACKAGES="IJulia BenchmarkTools"
# JULIA_PACKAGES_IF_GPU="CUDA" # or CuArrays for older Julia versions
# JULIA_NUM_THREADS=2
# #---------------------------------------------------#
# 
# if [ -z `which julia` ]; then
#   # Install Julia
#   JULIA_VER=`cut -d '.' -f -2 <<< "$JULIA_VERSION"`
#   echo "Installing Julia $JULIA_VERSION on the current Colab Runtime..."
#   BASE_URL="https://julialang-s3.julialang.org/bin/linux/x64"
#   URL="$BASE_URL/$JULIA_VER/julia-$JULIA_VERSION-linux-x86_64.tar.gz"
#   wget -nv $URL -O /tmp/julia.tar.gz # -nv means "not verbose"
#   tar -x -f /tmp/julia.tar.gz -C /usr/local --strip-components 1
#   rm /tmp/julia.tar.gz
# 
#   # Install Packages
#   nvidia-smi -L &> /dev/null && export GPU=1 || export GPU=0
#   if [ $GPU -eq 1 ]; then
#     JULIA_PACKAGES="$JULIA_PACKAGES $JULIA_PACKAGES_IF_GPU"
#   fi
#   for PKG in `echo $JULIA_PACKAGES`; do
#     echo "Installing Julia package $PKG..."
#     julia -e 'using Pkg; pkg"add '$PKG'; precompile;"' &> /dev/null
#   done
# 
#   # Install kernel and rename it to "julia"
#   echo "Installing IJulia kernel..."
#   julia -e 'using IJulia; IJulia.installkernel("julia", env=Dict(
#       "JULIA_NUM_THREADS"=>"'"$JULIA_NUM_THREADS"'"))'
#   KERNEL_DIR=`julia -e "using IJulia; print(IJulia.kerneldir())"`
#   KERNEL_NAME=`ls -d "$KERNEL_DIR"/julia*`
#   mv -f $KERNEL_NAME "$KERNEL_DIR"/julia
# 
#   echo ''
#   echo "Successfully installed `julia -v`!"
#   echo "Please reload this page (press Ctrl+R, ⌘+R, or the F5 key) then"
#   echo "jump to the 'Checking the Installation' section."
# fi

"""# Checking the Installation
The `versioninfo()` function should print your Julia version and some other info about the system:
"""

versioninfo()

using BenchmarkTools

M = rand(2^11, 2^11)

@btime $M * $M;

try
    using CUDA
catch
    println("No GPU found.")
else
    run(`nvidia-smi`)
    # Create a new random matrix directly on the GPU:
    M_on_gpu = CUDA.CURAND.rand(2^11, 2^11)
    @btime $M_on_gpu * $M_on_gpu; nothing
end

"""# Need Help?

* Learning: https://julialang.org/learning/
* Documentation: https://docs.julialang.org/
* Questions & Discussions:
  * https://discourse.julialang.org/
  * http://julialang.slack.com/
  * https://stackoverflow.com/questions/tagged/julia

If you ever ask for help or file an issue about Julia, you should generally provide the output of `versioninfo()`.

Add new code cells by clicking the `+ Code` button (or _Insert_ > _Code cell_).

Have fun!

<img src="https://raw.githubusercontent.com/JuliaLang/julia-logo-graphics/master/images/julia-logo-mask.png" height="100" />
"""

import Pkg; Pkg.add("MAT")

import Pkg; Pkg.add("JuMP")

import Pkg; Pkg.add("Symbolics")

import Pkg; Pkg.add("SymPy")

import Pkg; Pkg.add("PyPlot")

using MAT
using Random
using LinearAlgebra
using JuMP
using Symbolics
using SymPy
using PyPlot

rng = MersenneTwister(1234);
fileIn = matopen("CYLINDER_ALL.mat")
dset_JOEL = read(fileIn,"UALL")
close(fileIn)

snaps_have=125;
knowpart=dset_JOEL[:,1:snaps_have];
paddingpart=randn(rng, (89351, 151-snaps_have));
paddingpart_transpose=paddingpart';
pinv_paddingpart_transpose=pinv(paddingpart_transpose);

W=[dset_JOEL[:,1:snaps_have] pinv_paddingpart_transpose];

TotalSnapshots = size(W,2);
TotalKernels = size(W,2) - 1;
mu = 5.00;

x= Sym("x"); y= Sym("y"); Kernel(x,y)=exp(-1/mu*norm(x-y));

GramMatrix=[Kernel(W[:,i],W[:,j]) for i in 1:TotalKernels, j in 1:TotalKernels];
InteractionMatrix=[Kernel(W[:,i],W[:,j+1]) for i in 1:TotalKernels, j in 1:TotalKernels];

D=eigvals(pinv(GramMatrix)*InteractionMatrix);#eigen-values
D=Diagonal(D);#diagonal matrix of eigen-values
V=eigvecs(pinv(GramMatrix)*InteractionMatrix);#eigen-vectors
V=[V[i,j]/sqrt(V[:,j]'*GramMatrix*V[:,j]) for i in 1:size(V,2), j in 1:size(V,2)]; #normalization

KoopmanModes = pinv(GramMatrix*V)*W[:,1:end-1]';
KoopmanModes = KoopmanModes';#Koopman-Modes

img=imshow(real(reshape(KoopmanModes[:,61],(199,:))))
colorbar()
title("Koopman Mode(s)-150 with 151 snaps")

#colormap=:cividis #meh!
#colormap=(:inferno)#choice of interest
colormap=(:gnuplot)#choice of interest
#colormap=(:gnuplot2)#choice of interest
#colormap=(:magma)#choice of interest
#colormap=(:plasma)#choice of interest
#colormap=(:hot)#choice of interest
#colormap=(:bwr)#only for scientific purpose
#colormap=:Wistia
#colormap=:brg
#colormap=:winter
#colormap=:nipy_spectral

img=matplotlib.pyplot.imshow(imag(reshape(KoopmanModes[:,61],(199,:))),colormap)
colorbar()
title("Koopman Mode(s)-61 with 3 snaps")
