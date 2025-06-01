{pkgs}: {
  deps = [
    pkgs.glibcLocales
    pkgs.vimPlugins.vim-autoformat
    pkgs.haskellPackages.compdata-automata
    pkgs.automaticcomponenttoolkit
    pkgs.haskellPackages.automaton
  ];
}
