# lol-highlights-enhancer

This is a program meant to make things easier when it comes to dealing with League of Legends highlights.
It provides
additional context and functions that make sharing and management of highlights easier.

## Features
1. Provides additional information like the champion you were playing as, the outcome of the game and the game mode.
2. Works around the bug in the replay tool that prevented more than one highlight being recorded per replay session. 
3. Enables easy uploading to either Gfycat and Streamable.
4. Automatically pauses any pending uploads if a user starts a match and resumes when the match ends.
5. Allows for automatic uploads of highlights after watching a replay.

**At the time of writing this, patch notes for Patch 9.2 are out and the bug described in number 2 above is indicated as being
fixed. The work around implemented will coexist with this fix. (Further description below)**

## Running the Program
The application currently only supports Windows. There is a [portable zip](https://github.com/vickz84259/lol-highlights-enhancer/releases/download/1.0.0-alpha/LHE.zip) containing a prebuilt available on the releases section. 
### Steps
1. Unzip the file.
2. Run LHE.exe

You can start the application first or the League of Legends Client, the order doesn't matter.'

When starting the application for the first time, the application will try and retrieve match details for each highlight and will
notify you once it's done via the status bar at the bottom. You can still click and upload any highlight you want as it processes
the match details.

To have it automatically upload highlights, enable the setting as indicated in the screenshots below. Then open a 
replay while the application is running in the background (or minimised to the taskbar). Once you are done watching the replay,
any highlights created will be uploaded as per your settings.

## Running from Source
The application runs on Python 3.6 or higher

1. Clone the repository
```
git clone https://github.com/vickz84259/lol-highlights-enhancer.git
```
2. Install the dependencies **Note: It is advisable to install the dependencies in a virtual environment.**
```
pip install -r requirements.txt
```
3. Launch the application
```
python gui.py
```
4. (Optional) Building an executable. Run this in the project directory
```
pyinstaller lhe.spec
```
The resultant executable will be contained in `dist/LHE`

## Notes
If you encounter any issues of the client being unresponsive or generally not working as intended. Do consider running the
application from source as indicated in the section above.

The reason there are two buttons related to Gfycat is because for some reason, when you upload to gfycat, some times the link to the video
takes like 5 minutes before the video popups. It throws up 404 errors during that period. Like in this pic
![Desktop Screenshot](https://i.imgur.com/nzUhAlE.png)
So the other link acts as a _"Your video has been uploaded but gfycat aren't playing nice"_ button and shows you an alternative 
link to your gfycat upload. I am yet to understand how the alternate links work fine but the main link takes that long to show up.

## Screenshots
On first run the application will retrieve the match details from the highlights. Match details will not be provided for highlights
that have been renamed.
![Image 1](https://i.imgur.com/tDbm5p1.png)

When it's done retrieving the highlights.
![Image 2](https://i.imgur.com/WLkFaVv.png)

By default the application does not upload highlights automatically after they've been created. This setting controls that.
![Image 3](https://i.imgur.com/K0ODThY.png)

You can select one of the two or both of them.
![Image 4](https://i.imgur.com/I6STgFN.png)

![Image 5](https://i.imgur.com/Fatl9LJ.png)

## Dev Journey
This being my first GUI application to make, it was a bit of a challenge getting some concepts down. I'm mainly a backend dev so
this was uncharted territory. I decided to use Python since it's what I'm most familiar with. I decided on using Qt for Python
cause it seemed simplest to grasp but with the possibility of enabling me to do so much.

When Riot's API challenge was announced, I knew I had to make some thing to make sharing of highlights easier. Uploading 
highlights was one of the first features I thought of (but surprisingly among the last one to be fully implemented). 
Before all this, I had encountered a bug with the replay tool. When creating highlights during a particular replay session,
no matter how many highlights you create, the tool would end up overwriting them on top of each other. In the end you'd end up
with only one highlight, the last one. So, I set out to 'fix' this. Initially I thought that the replay tool sent an event to
the client whenever a highlight was created.

During my search for the event, I discovered certain events that indicated the user was watching a replay and when they were done.
I decided to use this instead. So now, the application listens to the websocket for the watching event and fires up a thread that
monitors the highlights folder. For any highlight created, it renamed it to the next identifying integer. e.g
> 7-10_EUW1-3191607521_01.webm > 7-10_EUW1-3191607521_02.webm

Then it uses the new file to determine what value the next higlight will be incremented to. When the user is done watching, the
replay, the application decremented the file names to achieve a normal ordering.
Later I realised that if the bug gets fixed it would clash :) with this workaround. So a workaround was to have the first highlight created be incremented by a 100 then incrementing by 1 for the subsequent ones.

Another challenge came when I was implementing the server side logic (Which can be seen [here](https://github.com/vickz84259/personal_website/tree/dev)). Since I needed to retrieve match details,
having a server proxy the requests would help secure the API token. I didn't want to use a library since I only needed to access
two endpoints. The problem with that is that I had to implement rate-limiting on my own, something I'd never done before. Continuing with
the trend of firsts, I ended up using Redis for the first time to implement the rate-limiting. I went for Redis cause a 
key-value store seemed fitting for this use case plus it looked easy enough to be implemented withing the short time I had.

I haven't tested my rate-limiting implementation but the 2 glances I've given it makes me believe it'll hold up. One thing that
makes me comfortable is having a CDN caching requests. When implementing the rate-limiting, I'd forgotten all about it. It was 
only when I was going through server logs and not seeing requests reaching the server, did I remember about it. 
Seeing the analytics from during the development of this application, I can rest easy at night.
![Cloudflare analytics](https://i.imgur.com/k9MxY89.png)

A challenge I also faced was how to protect the api secrets. The RIOT api key was already secure on the server as indicated above,
but for the secrets  required to upload the videod to their respective platforms I had to come up with something.
I ended up having that the server retrieves the summoner details, use the summoner's PUUID to encrypt the secrets. The client
stores the encrypted secrets in the Windows Vault.
The secrets are only decrypted when they are to be used. I am still looking for ways to enhance this further and ensure they are
more secure.

The last major challenge has been dealing with different threads and trying to make sure the main GUI thread remained responsive.
As I stated earlier this was my first time making a serious GUI application, so communicating between different threads and 
coordinating what should run when or after what, was the source of many bugs. I wanted to make sure I had a running application 
that during submission for the API challenge and afterwards the app would be useable by me or anyone else without hustle.
So if I couldn't guarantee the implementation of a feature to be solid, I didn't go with the implementation.

### Funny Bit
During development, I usually didn't have the application running for long periods. But when I was testing the ability to pause and 
resume uploads, I had to play a match. The test went well but I found out after the match that the application was competing
with Chrome on who would use the most RAM. It was using well over 1.5 GB due to having some unnecesarry thread sill running. The
thread was spawning, new shell processes every few seconds. XD

At the end of it all, I had fun and it was a great learning experience. I wasn't able to fully
implement every feature that I could have wanted but I'll definitely implement them down the road as this is a tool I've always
personally wanted.

## Future Considerations
1. Adding the ability to search/filter out highlights.
2. Uploading to more video platform sites and also social platforms.
3. Extract more context of what's going on from the video itself.
4. Multi selection and upload of highlights
