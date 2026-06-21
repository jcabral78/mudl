{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      pythonLibs = pkgs.python312.withPackages (ps: with ps; [
        yt-dlp
        requests
      ]);
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pkgs.python312
          pythonLibs
        ];
      };
    };
}
