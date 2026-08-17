{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      pythonLibs = pkgs.python3.withPackages (ps: with ps; [
        yt-dlp
        pyacoustid
      ]);
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          pythonLibs
          pkgs.chromaprint
          pkgs.ffmpeg
        ];
      };
    };
}
