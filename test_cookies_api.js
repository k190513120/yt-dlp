// JavaScript示例：使用cookies调用yt-dlp API

// API配置
const API_BASE_URL = 'https://yt-dlp-api-miaomiaocompany-3d8d2eee.koyeb.app';

// 示例cookies内容（用户提供的实际cookies）
const COOKIES_TEXT = `# Netscape HTTP Cookie File
# \`http://curl.haxx.se/rfc/cookie_spec.html\`
# This is a generated file!  Do not edit.

.youtube.com	TRUE	/	TRUE	1791794271	PREF	f4=4000000&tz=Asia.Shanghai
.youtube.com	TRUE	/	TRUE	1761199958	LOGIN_INFO	AFmmF2swRQIgNUB6ldF3L31sWs_9SclXXjyxszRxy4NzvLQtFt5U8r4CIQCFHwkaUYhrmOgzMZf27cxmu2jlTVUOzTr-lB6ktRQFTw:QUQ3MjNmeFFGa1NjM09uOFU4Z2ZiTkFfU2JUaGNGdGxxQmF2MkRYY3R6LVRsMmlEUGZtVHpqLXNWa3JobWcxVDFQekptR0VMRHZGTGt2STNMN21sT05nMlowX1lFSWNydGFONGMzUHBtVWFCVTduRkNQQUJ6d3RuZUVId2xmazBtRUFQb3lNUU9hMUpFUlBJZVhwaTNjcnlkOWt2bmJKeXln
.youtube.com	TRUE	/	FALSE	1790642899	HSID	AXfqeuUzr7J96ahXz
.youtube.com	TRUE	/	TRUE	1790642899	SSID	AgdmyGSM3MGwFbYex
.youtube.com	TRUE	/	FALSE	1790642899	APISID	6H6xpn_QLEOTXnHX/ALqMGGqeq02fzs3F7
.youtube.com	TRUE	/	TRUE	1790642899	SAPISID	J9A4cZJ8lhWF3Qly/AvxAwIROlDJuuTHUv
.youtube.com	TRUE	/	TRUE	1790642899	__Secure-1PAPISID	J9A4cZJ8lhWF3Qly/AvxAwIROlDJuuTHUv
.youtube.com	TRUE	/	TRUE	1790642899	__Secure-3PAPISID	J9A4cZJ8lhWF3Qly/AvxAwIROlDJuuTHUv
.youtube.com	TRUE	/	FALSE	1790642899	SID	g.a0000ggOvPuGe5ao1bVfYQlUkQYPvVtLhfdQvGcXxH_-PVSv5-bjqoWdtzWbx4awF8QhQcA2GAACgYKATQSARUSFQHGX2MiEs98yWefz3qlq5ff-F2IZxoVAUF8yKpu-7_RxQyXKzlHJiTbnY1S0076
.youtube.com	TRUE	/	TRUE	1790642899	__Secure-1PSID	g.a0000ggOvPuGe5ao1bVfYQlUkQYPvVtLhfdQvGcXxH_-PVSv5-bjGpNGyLLUWkJg47THarFHZwACgYKAf4SARUSFQHGX2Mi9UWqXH_kFfl8iV70FLHomBoVAUF8yKo9raZtWYOqQ7_r2qgVMBHE0076
.youtube.com	TRUE	/	TRUE	1790642899	__Secure-3PSID	g.a0000ggOvPuGe5ao1bVfYQlUkQYPvVtLhfdQvGcXxH_-PVSv5-bjElI8IhIS3_T4qS3ZzgwNRgACgYKAS0SARUSFQHGX2MiAqkoKrykjNb2DQQEnLHTGRoVAUF8yKrpABkm-dhrje0Ddpm0JbZo0076
.youtube.com	TRUE	/	FALSE	1787629522	SIDCC	AKEyXzWfaVWnMS_LkIjAgMyYUC3MPdBmxDeMPL8FpmELSUa5RxW7_pe8NdXW72TgdRLt8KBKog
.youtube.com	TRUE	/	TRUE	1787629522	__Secure-1PSIDCC	AKEyXzXYNjuNPxrKheBnqQgU2CFyU07N6t2TaeNvLzhcEKOlDVpRzsSycl0HktkXrgO-ugBxuQ
.youtube.com	TRUE	/	TRUE	1788578499	__Secure-3PSIDCC	AKEyXzXMmHqrsOrKfTWETMZzV_g3WjFLx9JxTaNtdw8E_09F4WtL4Eapm4sKix0dGN6zTvHCAzE
.youtube.com	TRUE	/	TRUE	1788770052	__Secure-1PSIDTS	sidts-CjEB5H03PzmsZTX-xFY0DHDiwQPEQ1Af5Zxo70i0f6VGB3OQSzwFddOd2u95aVV2IM7ZEAA
.youtube.com	TRUE	/	TRUE	1788770052	__Secure-3PSIDTS	sidts-CjEB5H03PzmsZTX-xFY0DHDiwQPEQ1Af5Zxo70i0f6VGB3OQSzwFddOd2u95aVV2IM7ZEAA
.youtube.com	TRUE	/	TRUE	1772786268	VISITOR_INFO1_LIVE	mMlisnI-vXU
.youtube.com	TRUE	/	TRUE	1772786268	VISITOR_PRIVACY_METADATA	CgJDThIEGgAgaQ%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	UwSy650qzIM
.youtube.com	TRUE	/	TRUE	1772784727	__Secure-ROLLOUT_TOKEN	CIDYvPiSwumi4gEQ6cWEquH0iwMY6a_3g5rGjwM%3D`;

// 获取视频流链接的函数
async function getStreamLinks(videoUrl, useCookies = true) {
    try {
        const requestBody = {
            url: videoUrl
        };
        
        // 如果使用cookies，添加到请求体中
        if (useCookies) {
            requestBody.cookies_text = COOKIES_TEXT;
        }
        
        const response = await fetch(`${API_BASE_URL}/api/stream-links`, {
            method: 'POST',
            headers: {
                'Content-