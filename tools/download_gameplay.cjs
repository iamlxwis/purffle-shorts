#!/usr/bin/env node
// Download only the fixed, user-authorized gameplay video.
const fs = require('node:fs');
const path = require('node:path');
const ytdl = require('@distube/ytdl-core');
const url = 'https://youtu.be/s3_xa3qdsks';
const target = process.argv[2] || 'media/backgrounds/youtube-gameplay.mp4';
async function main() {
  fs.mkdirSync(path.dirname(target), {recursive:true});
  const info = await ytdl.getInfo(url);
  const formats = info.formats.filter(f => f.container === 'mp4' && f.hasVideo && f.hasAudio && Number(f.contentLength || 0) <= 350000000);
  if (!formats.length) throw new Error('No suitable progressive MP4 format; refusing incomplete gameplay download');
  const format = formats.sort((a,b)=>(b.height||0)-(a.height||0))[0];
  const tmp = target + '.part';
  try {
    await new Promise((resolve,reject)=>{
      const stream = ytdl.downloadFromInfo(info, {format});
      const out = fs.createWriteStream(tmp);
      stream.on('error',reject);out.on('error',reject);out.on('finish',resolve);
      stream.pipe(out);
    });
    if (fs.statSync(tmp).size < 100000) throw new Error('Downloaded video is unexpectedly small');
    fs.renameSync(tmp,target);
    console.log('Downloaded authorized gameplay MP4:',target);
  } catch(e) { try{fs.unlinkSync(tmp)}catch{};throw e; }
}
main().catch(e=>{console.error('npm YouTube downloader failed:',e.message);process.exitCode=1});
