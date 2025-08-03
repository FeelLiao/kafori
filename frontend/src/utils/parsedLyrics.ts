// import { API } from "@/api/interface";
export interface LyricLine {
    time: number; // 歌词对应的时间（毫秒）
    lrc: string; // 原文歌词文本
    tlyric: string; // 翻译文本
    romaLrc: string; // 罗马音歌词
}

export function parseLyrics(lyricString: string): LyricLine[] {
    if (!lyricString) return [{ time: 0, lrc: '暂无歌词', tlyric: '暂无歌词', romaLrc: '暂无歌词' }];

    // 假设 decodeBase64 是一个函数，用于解码 Base64 字符串
    const decodedLyrics = decodeBase64(lyricString);
    const lines = decodedLyrics.split('\n');
    const parsedLines: LyricLine[] = [];

    lines.forEach((line) => {
        // 匹配时间戳
        const matches = [...line.matchAll(/\[(\d{2}):(\d{2})\.(\d{2,3})\]/g)];
        // 去除时间戳部分，保留歌词文本
        const content = line.replace(/\[.*?\]/g, '').trim();

        // 如果有时间戳且内容不为空
        if (matches.length && content) {
            matches.forEach((match) => {
                const minutes = parseInt(match[1], 10);
                const seconds = parseInt(match[2], 10);
                const milliseconds = match[3].length === 3 ? parseInt(match[3], 10) : parseInt(match[3], 10) * 10;
                const time = minutes * 60 * 1000 + seconds * 1000 + milliseconds;

                // 分割原文歌词和翻译歌词
                const parts = content.split(/\s{2,}/); // 通过两个或更多空格分割
                const lrc = parts[0] || ''; // 原文歌词
                const tlyric = parts[1] || ''; // 翻译歌词
                const romaLrc = parts[2] || ''; // 罗马音歌词（如果有）

                parsedLines.push({ time, lrc, tlyric, romaLrc });
            });
        }
    });

    return parsedLines;
}


export function decodeBase64(base64String) {
    try {
        // 使用 atob 函数解码 Base64 字符串
        const decodedString = atob(base64String);

        // 将 UTF-16 编码的字符串转换为 UTF-8 编码的文本
        const bytes = new Uint8Array(decodedString.length);
        for (let i = 0; i < decodedString.length; i++) {
            bytes[i] = decodedString.charCodeAt(i);
        }

        const decoder = new TextDecoder('utf-8');
        const utf8String = decoder.decode(bytes);

        return utf8String;
    } catch (error) {
        console.error('解码失败:', error);
        return null;
    }
}

// export function parseAndMergeLyrics(lyrics: string): LyricData {
//     const { lyricUser, transUser, lrc, tlyric, romalrc } = lyrics
//
//     // 解析原歌词、翻译歌词和罗马音歌词
//     const originalParsed: LyricLine[] = parseLyrics(lrc?.lyric ?? '') || []
//     const translatedParsed: LyricLine[] = parseLyrics(tlyric?.lyric ?? '') || []
//     const romaParsed: LyricLine[] = parseLyrics(romalrc?.lyric ?? '') || []
//
//     // 备注信息，如果 originalParsed 为空，将 lrc.lyric 作为备注显示
//     let remark = ''
//     if (originalParsed.length === 0 && lrc?.lyric) {
//         remark = lrc.lyric // 使用 lrc.lyric 作为备注
//     }
//
//     // 合并原文和翻译，假设每一行的时间戳都一致
//     const mergedLyrics = originalParsed.map((lyric) => {
//         // 尝试找到时间戳匹配的翻译行
//         const translation: LyricLine | undefined = translatedParsed.find(
//             (tran) => tran.time === lyric.time
//         )
//
//         const romaLrc: LyricLine | undefined = romaParsed.find(
//             (tran) => tran.time === lyric.time
//         )
//
//         // 如果找到翻译，添加到原文对象中
//         return {
//             ...lyric,
//             tlyric: translation?.lrc,
//             romaLrc: romaLrc?.lrc,
//         }
//     })
//
//     // 如果也没有解析到原歌词，同时歌词字段不为空，使用 lyric 字段作为备注
//     if (mergedLyrics.length === 0 && lyrics.lyric) {
//         remark = lyrics.lyric
//     }
//
//     return {
//         lines: mergedLyrics,
//         lyricUser: lyricUser || '',
//         transUser: transUser || '',
//         remark,
//     }
// }



