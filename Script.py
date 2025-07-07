class script(object):
    START_TXT = """🎬 <b>Hey there, {}</b>! 

🤖 I'm <b>{}</b> - Your Personal Movie & Subtitle Bot!

✨ <b>What I Can Do:</b>
🎥 Search 16,000+ Movies & Series
🌍 Multi-Language Subtitles (14 Languages)
⚡ Fast Download Links
🎭 HD Quality Films

🚀 <b>How to Use:</b>
1️⃣ Type any movie name
2️⃣ Select your subtitle language
3️⃣ Get Movie + Subtitle files instantly!

💡 <b>Pro Tip:</b> Join updates channel for latest movies!"""

    
    HELP_TXT = """Hello {}!
    
Here αre тнe αvαιlαвle coммαɴdѕ.
    
I’м нere тo αѕѕιѕт yoυ! Feel ғree тo αѕĸ ғor αɴy ɢυιdαɴce or coммαɴdѕ yoυ мαy ɴeed.
Leт’ѕ мαĸe тнιɴɢѕ eαѕιer ғor yoυ!"""


    ABOUT_TXT = """Here are some details you need to know.

✯ 𝙱𝙾𝚃 𝚃𝚈𝙿𝙴: Movie Bot with Subtitle System
✯ 𝙳𝙴𝚅𝙴𝙻𝙾𝙿𝙴𝚁: <a href="https://t.me/Iron_voldy">Hasindu Theekshana</a>
✯ 𝙶𝙸𝚃𝙷𝚄𝙱: <a href="https://github.com/Iron-voldy">Iron-voldy</a> 
✯ 𝙵𝙴𝙰𝚃𝚄𝚁𝙴𝚂: Movies + Multi-Language Subtitles
✯ 𝚂𝚄𝙱𝚃𝙸𝚃𝙻𝙴𝚂: 14 Languages Supported """  

      
    MANUELFILTER_TXT = """Help: <b>Filters</b>
- Fιlтerѕ αllow υѕerѕ тo ѕeт αυтoмαтed replιeѕ ғor ѕpecιғιc ĸeywordѕ, αɴd тнe вoт wιll reѕpoɴd wнeɴever α ĸeyword ιѕ ғoυɴd ιɴ тнe мeѕѕαɢe.

<b>NOTE:</b>
1. Tнιѕ вoт ѕнoυld нαve αdмιɴ prιvιleɢeѕ тo ғυɴcтιoɴ properly.  
2. Oɴly αdмιɴѕ cαɴ αdd ғιlтerѕ ιɴ α cнαт.  
3. Alerт вυттoɴѕ нαve α lιмιт oғ 64 cнαrαcтerѕ.


<b>Coммαɴdѕ αɴd Uѕαɢe:</b>
/filter - <code>Add a filter in a chat.</code>  
/filters - <code>List all the filters in a chat.</code>  
/del - <code>Delete a specific filter in a chat.</code>  
/delall - <code>Delete all filters in a chat (chat owner only).</code>  """


    BUTTON_TXT = """Help: <b>Buttons</b>
- Tнe вoт ѕυpporтѕ вoтн URL αɴd αlerт ιɴlιɴe вυттoɴѕ.

<b>NOTE:</b>
1. Teleɢrαм wιll ɴoт αllow yoυ тo ѕeɴd вυттoɴѕ wιтнoυт αɴy coɴтeɴт, ѕo coɴтeɴт ιѕ мαɴdαтory.  
2. Tнe вoт ѕυpporтѕ вυттoɴѕ wιтн αɴy тype oғ Teleɢrαм мedια.  
3. Bυттoɴѕ ѕнoυld вe properly pαrѕed ιɴ мαrĸdowɴ ғorмαт.

<b>URL Buttons:</b>
<code>[Button Text](buttonurl:https://t.me/SECLK)</code>

<b>Alert Buttons:</b>
<code>[Button Text](buttonalert:This is an alert message, You should use @NETFLIXLKBOT to get Movies)</code>"""


    AUTOFILTER_TXT = """Help: <b>Auto Filter</b>

<b>NOTE:</b>
1. Mαĸe мe тнe αdмιɴ oғ yoυr cнαɴɴel ιғ ιт'ѕ prιvαтe.  
2. Mαĸe ѕυre тнαт yoυr cнαɴɴel doeѕ ɴoт coɴтαιɴ cαмrιpѕ, porɴ, or ғαĸe ғιleѕ.  
3. Forwαrd тнe lαѕт мeѕѕαɢe тo мe wιтн qυoтeѕ.

I’ll αdd αll тнe ғιleѕ ιɴ тнαт cнαɴɴel тo мy dαтαвαѕe."""

    
    CONNECTION_TXT = """Help: <b>Connections</b>

- Uѕed тo coɴɴecт тнe вoт тo PM ғor мαɴαɢιɴɢ ғιlтerѕ.
- Helpѕ αvoιd ѕpαммιɴɢ ιɴ ɢroυpѕ.

<b>NOTE:</b>
1. Oɴly αdмιɴѕ cαɴ αdd α coɴɴecтιoɴ.
2. Seɴd <code>/connect</code> ғor coɴɴecтιɴɢ мe тo yoυr PM.

<b>Commands and Usage:</b>
/connect  - <code>Connect a particular chat to your PM</code>
/disconnect  - <code>Disconnect from a chat</code>
/connections  - <code>List all your connections</code>"""

    EXTRAMOD_TXT = """Help: <b>Extra Modules</b>

<b>NOTE:</b>
Tнeѕe αre αddιтιoɴαl ғeαтυreѕ oғ тнe Teѕѕα вoт тo eɴнαɴce yoυr eхperιeɴce.

<b>Commands and Usage:</b>
/id - <code>Retrieve the ID of a specified user.</code>
/info - <code>Get detailed information about a user.</code>
/imdb - <code>Fetch film information from IMDb.</code>
/search - <code>Search for film details across multiple sources.</code>

Feel ғree тo υѕe тнeѕe coммαɴdѕ тo eхplore тнe вoт'ѕ cαpαвιlιтιeѕ ғυrтнer! 📚"""


    ADMIN_TXT = """Help: <b>Admin Mods</b>

<b>NOTE:</b>
Tнιѕ мodυle ιѕ eхclυѕιvely ғor вoт αdмιɴιѕтrαтorѕ oɴly. Uѕe тнeѕe coммαɴdѕ тo мαɴαɢe υѕerѕ αɴd cнαт operαтιoɴѕ eғғecтιvely.

<b>Commands and Usage:</b>
/users - <code>Retrieve a list of all users and their IDs.</code>
/chats - <code>Get a list of all chats and their IDs.</code>
/leave - <code>Leave a specified chat.</code>
/unban - <code>Unban a previously banned user.</code>
/channel - <code>Get a list of all connected channels.</code>
/broadcast - <code>Broadcast a message to all users.</code>

Uѕe тнeѕe αdмιɴ coммαɴdѕ тo мαɴαɢe yoυr вoт eғғecтιvely αɴd ĸeep everyтнιɴɢ rυɴɴιɴɢ ѕмooтнly! 📊"""

    
    STATUS_TXT = """- 𝙵𝚒𝚕𝚎 𝙳𝚊𝚝𝚊𝚋𝚊𝚜𝚎 𝟷.𝟶 -
★ ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ: <code>{}</code>
★ ᴜꜱᴇᴅ ꜱᴛᴏʀᴀɢᴇ: <code>{}</code>

- 𝙵𝚒𝚕𝚎 𝙳𝚊𝚝𝚊𝚋𝚊𝚜𝚎 𝟸.𝟶 -
★ ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ: <code>{}</code>
★ ᴜꜱᴇᴅ ꜱᴛᴏʀᴀɢᴇ: <code>{}</code>

- 𝚄𝚜𝚎𝚛 𝙳𝚊𝚝𝚊𝚋𝚊𝚜𝚎 𝟷.𝟶 -
★ ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: <code>{}</code>
★ ᴛᴏᴛᴀʟ ᴄʜᴀᴛꜱ: <code>{}</code>
★ ᴜꜱᴇᴅ ꜱᴛᴏʀᴀɢᴇ: <code>{}</code>

- 𝚂𝚎𝚛𝚟𝚎𝚛 𝚁𝚎𝚜𝚘𝚞𝚛𝚌𝚎𝚜 -
★ ᴛᴏᴛᴀʟ ʀᴀᴍ: <code>{}</code>
★ ᴜsᴇᴅ ʀᴀᴍ: <code>{}</code>"""

    LOG_TEXT_G = """#NewGroup
Group = {}(<code>{}</code>)
Total Members = <code>{}</code>
Added By - {}
"""
    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Name - {}
"""
    
    REQINFO = """
⚠ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ⚠
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯
ɪꜰ ʏᴏᴜ ᴅᴏ ɴᴏᴛ ꜱᴇᴇ ᴛʜᴇ ʀᴇǫᴜᴇsᴛᴇᴅ ᴍᴏᴠɪᴇ / sᴇʀɪᴇs ꜰɪʟᴇ, 
ɢᴏ ᴛᴏ ɢᴏᴏɢʟᴇ ➠ ᴛʏᴘᴇ ᴍᴏᴠɪᴇ ᴏʀ ꜱᴇʀɪᴇꜱ ɴᴀᴍᴇ ➠ ᴄᴏᴘʏ ᴄᴏʀʀᴇᴄᴛ ɴᴀᴍᴇ ➠ ᴘᴀꜱᴛᴇ ᴛʜɪꜱ ɢʀᴏᴜᴘ"""

    MINFO = """
ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯
ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴀ ᴍᴏᴠɪᴇ ғᴏʟʟᴏᴡ ᴛʜᴇ ғᴏʀᴍᴀᴛ ʙᴇʟᴏᴡ
𝐔𝐧𝐜𝐡𝐚𝐫𝐭𝐞𝐝 | 𝐃𝐮𝐧𝐞 𝟐𝟎𝟐𝟏 | 𝐓𝐫𝐨𝐥𝐥 𝟐𝟎𝟐𝟐 𝟕𝟐𝟎𝐩

🚯 ᴅᴏɴᴛ ᴜꜱᴇ ➠ ':(!,./)"""

    SINFO = """
ꜱᴇʀɪᴇꜱ ʀᴇǫᴜᴇꜱᴛ ꜰᴏʀᴍᴀᴛ
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯
ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴀ sᴇʀɪᴇs ғᴏʟʟᴏᴡ ᴛʜᴇ ғᴏʀᴍᴀᴛ ʙᴇʟᴏᴡ
𝐋𝐨𝐤𝐢 𝐒𝟎𝟏𝐄𝟎𝟏 | 𝐘𝐨𝐮 𝐒𝟎𝟑 | 𝐖𝐞𝐝𝐧𝐞𝐬𝐝𝐚𝐲 𝐒𝟎𝟏 𝟕𝟐𝟎𝐩

🚯 ᴅᴏɴᴛ ᴜꜱᴇ ➠ ':(!,./)"""
    
    
    OWNER_INFO = """
<b>⍟───[ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴅᴇᴛᴀɪʟꜱ ]───⍟
⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯⋯    
• ꜰᴜʟʟ ɴᴀᴍᴇ : Hasindu Theekshana
• ᴛᴇʟᴇɢʀᴀᴍ : <a href='https://t.me/Iron_voldy'>@Iron_voldy</a>
• ɢɪᴛʜᴜʙ : <a href='https://github.com/Iron-voldy'>Iron-voldy</a>
• ᴅᴇᴠᴇʟᴏᴘᴇʀ : Movie Bot with Subtitle System</b>"""

    IMDB_TEMPLATE = """
🎬 <b><a href={url}>{title}</a> ({year})</b>  
‌‌‌‌<b>{runtime}min | {release_date}</b>  

‌‌‌‌<b>⭐️ IMDB</b> ➠ <b><i>{rating}/10 ({votes})</i></b>  
‌‌‌‌<b>🌏 Country</b> ➠ <b><i>{countries}</i></b>  
<b>🔉 Language</b> ➠ <b><i>{languages}</i></b>  
‌‌‌‌‌‌‌‌‌‌‌‌<b>⚙️ Genres</b> ➠ <b><i>{genres}</i></b>  

‌‌‌‌®️ <b><a href='https://t.me/SECL4U'>Mαιɴ Cнαɴɴel</a></b>
"""

    FILE_CAPTION = """➥ 𝗙𝗶𝗹𝗲 𝗡𝗮𝗺𝗲: <b>@SECL4U </b><code>{file_name}</code>

➠ 𝗛𝗮𝘃𝗶𝗻𝗴 𝗶𝘀𝘀𝘂𝗲: <a href='https://t.me/SECL4U/54'>𝙏𝙧𝙮 𝙖𝙣𝙤𝙩𝙝𝙚𝙧 𝙗𝙤𝙩</a>
➠ 𝗡𝗲𝘄 𝘁𝗼 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁: <a href='https://t.me/SECOfficial_Bot'>𝙒𝙖𝙩𝙘𝙝 𝙩𝙝𝙚 𝙜𝙪𝙞𝙙𝙚</a>
━━━━━━━━━━━━━━‌‌
🪫 𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗯𝘆: 
<b>- @SECLK | @CeylonCryptoSL -</b>"""

    BUTTON_LOCK_TEXT = """Please check that you have joined the required channels."""
    FORCE_SUB_TEXT = """Please join the required channels to use this bot."""
    WELCOM_TEXT = """Welcome to the bot! Use the commands to get started."""
