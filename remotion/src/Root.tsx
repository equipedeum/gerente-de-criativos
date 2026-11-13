import React, {useEffect, useState} from 'react';
import {Composition, continueRender, delayRender} from 'remotion';
import {carregarFontes} from './fontes';
import {DIM, PaperVideo} from './paper/PaperVideo';
import {PAPEIS} from './paper/videos';

const FPS = 30;

// Estilo papel (Editor Paper): um vídeo por arquivo em src/paper/videos/, registrado em src/paper/videos/index.ts.
// A Animação viral (3D) tem entrada própria: src/animada3d/index.tsx (bundle separado, pasta public-animada3d).
export const Root: React.FC = () => {
  const [handle] = useState(() => delayRender('carregar fontes'));
  useEffect(() => {
    carregarFontes().then(() => continueRender(handle));
  }, [handle]);

  return (
    <>
      {PAPEIS.map((v) => (
        <Composition
          key={v.nome}
          id={v.nome}
          component={PaperVideo}
          durationInFrames={Math.round(v.duracao * FPS)}
          fps={FPS}
          width={1080}
          height={1920}
          defaultProps={{nome: v.nome}}
        />
      ))}
      {/* Os outros formatos (YT/IN/GL): paper-<id>-YT etc., só depois do OK do RL. */}
      {PAPEIS.flatMap((v) =>
        (['YT', 'IN', 'GL'] as const).map((f) => (
          <Composition
            key={`${v.nome}-${f}`}
            id={`${v.nome}-${f}`}
            component={PaperVideo}
            durationInFrames={Math.round(v.duracao * FPS)}
            fps={FPS}
            width={DIM[f][0]}
            height={DIM[f][1]}
            defaultProps={{nome: v.nome, formato: f}}
          />
        )),
      )}
    </>
  );
};
