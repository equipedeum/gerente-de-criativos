// Entrada PRÓPRIA do estilo "Animação viral" (não passa pelo src/Root.tsx das outras composições: assim o bundle usa uma
// pasta public enxuta, remotion/public-animada3d, e o three.js não entra no bundle dos outros estilos).
// Vídeo novo = pasta src/animada3d/<id>/ (molde: exemplo/) + mais uma <Composition> aqui:
//   import { X_Animada3D, X_FRAMES } from "./<id>/Video";
//   <Composition id="<id>-animada3d" component={X_Animada3D} durationInFrames={X_FRAMES} fps={30} width={1080} height={1920} />
// Formatos (depois do OK do RL): "<id>-animada3d-IN|GL|YT" com defaultProps={{ formato: "IN" }} e width/height de FMT
// (ver a skill animacao-viral).
import React from "react";
import { registerRoot } from "remotion";

const Root: React.FC = () => <></>;
registerRoot(Root);
