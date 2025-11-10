# **Educational Video Generation**

## **Overview**

Develop a video generation pipeline that transforms text prompts into 80-180 second educational physics videos. Each video includes narration, timed visuals, and progressive text reveals with consistent styling. Content creators use this system to author curriculum videos for 17-year-old physics students.

Note: the Video\_Tips.md file along with this document can be used for inspiration but is not essential to follow. It was the Tips doc we had AI write for our current video gen process and are including it here for inspiration rather than a specific rubric to follow. 

## **Objective**

Build a reproducible tool that automatically compiles short educational videos from text-based specifications. The pipeline interprets input, generates narration and visuals, and assembles synced MP4 videos with unified visual identity.

## **Users**

* **Primary:** Internal content creators developing curriculum videos.

## **Success Criteria**

* Produce a video generation pipeline capable of creating infinite high-quality videos  
  * Measure success with 3 generated videos \- 1 for each of Newtons Laws of Motion, each 80-180s long and bug-free  
  * Start from a single prompt  
* Maintain style consistency across all videos (fonts, colors, pacing, voice, transitions)  
* Achieve audio-visual sync within ±300 ms  
* Ensure deterministic re-runs: same inputs yield similar outputs  
* Enable precise iteration without breaking existing work

## **Scope**

### **In Scope**

1. **Prompt expansion:** Input initial video idea and refine it into detailed specs (equations, narrative, examples, visuals, graphs)  
2. **Script generation:** Automatically produce narration text, visuals, locations, and timing  
3. **Narration synthesis:** Use ElevenLabs or OpenAI TTS synced with visuals at natural pace with pauses  
4. **Visual generation:** 2D animations with static diagrams (e.g. Manim), graphs and equations (Latex) drawn in real-time  
5. **Storyline:** Begin each video with real-world animation (rockets, balls, boats) to prime students for the lesson  
6. **Sync alignment:** Auto-match narration timestamps with text and visuals  
7. **Video assembly:** Combine narration, overlays, and visuals into 1080p MP4  
8. **Style system:** Define and apply consistent layout, font, color, and animation tokens  
9. **Iteration:** Reliable iteration with precise changes maintaining existing parameters; fast low-res preview before final high-res render  
10. **UI:** Functional interface for inputting prompts and other inputs (JSON, images)

## **Inputs & Outputs**

### **Inputs**

* **Skill Prompt:** Concise text prompt describing skill  
* **Other Spec:** Learning objective, script outline, visuals plan, timing cues, style profile, opening narrative, animations, images

### **Outputs**

* MP4 (1080p, 30 fps)  
* JSON (cue alignment metadata)  
* TXT (narration \+ on-screen text)  
* assets/ (auto-generated diagrams and animations)

## **Style Consistency System**

* **Typography:** One consistent font family and size system; all text easily readable  
* **Color Palette:** Defined accent and background tones with consistent lighting  
* **Transitions:** Uniform duration and easing (250-500 ms)  
* **Equations:** LaTeX → SVG with progressive draw; consistent variable color coding  
* **Graph Animations:** Sequential appearance of axes, units, data, highlights  
* **Voice Profile:** Same tone, pitch, and energy across videos  
* **Overlays:** No unintended overlap between text/figures

All style tokens stored in a file for deterministic reproduction.

### **Manual Checks**

* Narrative structure: clear beginning, explanation, example  
* Visual clarity and pacing  
* Consistent tone and voice  
* Engagement and conceptual accuracy

## **Current Approach**

We have currently been generating videos from Python scripts and Manim, by prompting Claude with a lesson plan. We are including an example python script and [generated video](https://youtu.be/flRi-NXoMdI) so that you can get insight to our current process, but the primary issues we are facing are:

1. This script is the result of quite a few iterations with Claude to fix overlapping features and audio/video sync.  
2. The final video is still not great quality (things are hard to read, pacing isn’t consistent, it requires several iterations to make simple changes like text position changes), and overall feels bland. 

NOTE: The video has some repetition (repeating conditions for horizontal and vertical motion) because we experimented with the order of presenting these skills to students. 

