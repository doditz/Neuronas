{pkgs}: {
  deps = [
    pkgs.glibcLocales
    pkgs.stdenv.cc.cc.lib
    pkgs.zlib
    pkgs.libffi
    pkgs.openssl
    pkgs.curl
    pkgs.git
    pkgs.gcc
    pkgs.pkg-config
    pkgs.python311Packages.pip
    pkgs.python311Packages.setuptools
    pkgs.python311Packages.wheel
    pkgs.vimPlugins.vim-autoformat
    pkgs.haskellPackages.compdata-automata
    pkgs.automaticcomponenttoolkit
    pkgs.haskellPackages.automaton
  ];
}