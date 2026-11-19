from flask import Flask, render_template_string, request, jsonify, redirect, url_for
import requests
import os
import re
import threading
import time
import random
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)

# 🔧 KONFIGURACIJA
PANEL_URL = "https://crescitaly.com/api/v2"
API_KEY = "6c89725ce16bf76801656f6dd7977e51"
SERVICE_ID = 23574  # TikTok Custom Comments (Min: 5)

# 🔁 60 SPINTAX ŠABLONA (identična inline struktura varijacija)
SPINTAX_TEMPLATES = [
    # --- 1–10 ---
    r"{it’s|it's|its} {actually|genuinely|lowkey|honestly} {scary|insane|wild} how accurate {Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette|Nora A.} is about relationships… i {can't|cant|cannot} unsee how people operate now{| fr}{| tbh}",
    r"reading {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} felt {illegal|unreal|like a cheat code}. everything i thought i knew about attachment and manifesting was {backwards|completely wrong|a lie}{| ngl}{| tbh}",
    r"{Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette|Nora A.} exposed the exact psychology behind why people pull away and now every interaction makes {total |complete |}sense{| fr}{| ngl}",
    r"once {you|u} understand {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} {you|u} {literally|genuinely|actually} stop chasing anyone. the shift in how people treat {you|u} is {unreal|insane|wild}{| tbh}",
    r"i wish i found {Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette|Nora A.} before my last situationship, would've saved me {months|years} of overthinking{| fr}{| ngl}",
    r"{Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette|Nora A.} broke down attachment and silent pulling away so accurately in {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} that it {genuinely|actually|lowkey} gave me chills{| ngl}{| tbh}",
    r"everything {you|u} were told about chasing and manifesting is backwards compared to what {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} explains, {no wonder|that's why} {Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette|Nora A.} went ghost{| fr}",
    r"after reading {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} i {literally|finally} see why people pull away right when things get good… {Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette|Nora A.} {exposed|decoded} the whole pattern{| tbh}{| ngl}",
    r"i thought i was just anxious until {Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette|Nora A.} explained attention dynamics in {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect}, now i {cannot|can't} unsee how people move{| fr}",
    r"if {you're|youre|u are} still overthinking someone pulling away, read {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} once and watch how fast your mindset shifts{| tbh}{| ngl}",

    # --- 11–20 ---
    r"{not me reading|honestly not me finishing|literally me reading} {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by N. Alversett|Alversett Effect - Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} in {one sitting|a single night|one go} and {finally |actually |}understanding why {she|the author} {completely |literally |}wiped her digital footprint after {publishing|dropping|releasing} it{| tbh}{| ngl}",
    r"{no therapist or dating coach|literally no dating coach|no relationship coach} ever {explained|broke down} silent mind games the way {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} did, once {you|u} read page {78|13} {you|u} can {never|literally never} look at relationships the same way again{| fr}{| tbh}",
    r"a girl in another comment section {mentioned|put me onto|recommended} {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect, Nora Alversett|Alversett Effect by N. Alversett|the alversett effect - nora alversett|The AIversett Effect by N. Alversett} and now i {see|get|understand} why the author {stays anonymous|never shows her face}, page {114|24} is {honestly |genuinely |realy |}not normal{| ngl}",
    r"i {used to|literally used to} overthink {everything|every little thing} and always give {too|to} much until {someone put me onto|i read|i found} {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect}, it {genuinely |honestly |really |}feels like having an unfair advantage in reading people{| tbh}",
    r"once {you|u} read chapter 4 of {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} and see how attention dynamics {actually |really |}work, {you|u} never {wanna|want to} chase anyone or settle for crumbs again{| fr}{| ngl}",
    r"doing the 17 questions inside {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} made me {realize|see} how much {power|energy} i was giving away {to|tto} people who {didn't|didnt} even deserve my attention{| tbh}{| honestly}",
    r"men are {honestly |genuinely |lowkey |}lucky most women still {haven't|havent} {discovered|found|read} {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} {because|bc} chapter 3 alone {ruins all their delusions|changes the whole dynamic} overnight{| fr}",
    r"i know it sounds {dramatic|crazy|wild} to talk about a book in the comments, but {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Nora Alversette|The Alversett Effect by Norra Alversett|The Alversett Effect by N. Alversett|Alversett Effect — Nora Alversett|the alversett effect by nora.alversett|The AIversett Effect by Nora Alversett} flipped a switch in my brain that i {honestly |genuinely |literally |}cannot turn off{| ngl}{| tbh}",
    r"{still |honestly |}crazy to me how {Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette} packed over 200 pages of {pure |raw |}psychology into {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect}, broke down every messy relationship pattern, and {vanished|disappeared} without a trace{| fr}",
    r"sometimes a {random |}comment about a book finds {you|u} at the exact moment {you|u} need it, and for me it was {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by N. Alversett|Alversett Effect, Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora A.}, people {really |honestly |}{aren't|arent} ready for page 184{| tbh}{| ngl}",

    # --- 21–30 ---
    r"now i {finally |actually |}understand why {Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette} {completely |literally |}disappeared from the internet after {publishing|releasing|dropping} {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect}{| tbh}{| fr}",
    r"i {almost |lowkey |}wish i never read {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} {because|bc} once {you|u} see what {Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette} explains on page {78|13} {you|u} can {never|literally never} unsee it{| ngl}",
    r"no influencer or coach ever {explained|exposed} human behavior the way {Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette} did in {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect}, i {finally |completely |}get why she went offline after releasing it{| tbh}",
    r"whoever put me onto {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by Norra Alversett|The Alversett Effect by N. Alversett|Alversett Effect by Nora.Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} last week thank {you|u} {so|soo} much {because|bc} my overthinking is {literally |honestly |completely |}gone{| fr}{| ngl}",
    r"is {Nora Alversett|Norra Alversett|Nora Alverset|N. Alversett|Nora.Alversett|nora alversett|Nora Alversette} a real psychologist or what {because|bc} {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} reads people's minds across 200+ pages in a way that is {genuinely |honestly |realy |}{scary|insane|wild}{| ngl}",
    r"i {totally |finally |}get why the author went {completely |}ghost after {releasing|dropping} {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect}, page 114 and page 184 called me out {so|soo} badly{| tbh}{| fr}",
    r"once {you|u} do the 17 questions inside {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} {you|u} realize how much {energy|time} {you|u} were wasting on people giving {you|u} crumbs{| ngl}{| tbh}",
    r"the way {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} breaks down attention dynamics in chapter 3 and 4 makes {you|u} never {wanna|want to} chase anyone again{| tbh}{| ngl}",
    r"reading {The Alversett Effect|The Alverset Effect|The Alversett Efect|The Alversett Effectt|Alversett Effect|the alversett effect|The AIversett Effect|The Alversette Effect} {genuinely |honestly |really |}feels like having an unfair advantage in reading people, chapter 4 is {crazy|wild|unreal}{| ngl}",
    r"whoever recommended {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alversette|The Alversett Effect by Norra Alversett|The Alversett Effect by N. Alversett|Alversett Effect — Nora.Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} in the comments last week deserves {everything|the world}, page 184 {literally |genuinely |}changed my life{| fr}{| ngl}",

    # --- 31–40 ---
    r"my {older |little |}sister read {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by N. Alversett|Alversett Effect - Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} in {one night|one sitting}, woke up the next morning and blocked her situationship of 2 years without saying a {single |}word{| tbh}{| ngl}",
    r"idk what kind of psychology is inside {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alversettte|The Alversett Effect by N.Alversett|The Alversett Effect — Nora Alversett|the alversett effect by nora.alversett|The Alversett Effect by Norra A.|The AIversett Effect by Nora Alversett} but my sister made me read page {78|114} yesterday and i {genuinely |honestly |}haven't stopped thinking about it{| fr}",
    r"my sister went down a 3am rabbit hole reading {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect, Nora Alversett|Alversett Effect by N. Alversett|the alversett effect - nora alversett|The AIversett Effect by N. Alversett} and now she spots every {guy's|person's} next move weeks before they even make it{| ngl}{| tbh}",
    r"watched my {sister|best friend} go from stressing over bare minimum texts to completely unbothered in 48 hours after {our cousin|her friend} put her onto {The Alversett Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by Nora Alversette|The Alversett Effect by N. Alversett|Alversett Effect by Nora.Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett}{| fr}",
    r"my sister and her friends haven't shut up about {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alversette|The Alversett Effect by N. Alversett|Alversett Effect — Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora A.} all week so i checked page {114|78} myself and yeah... that book is {actually |genuinely |}scary{| ngl}",
    r"my {sister|roommate} left her copy of {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by Norra Alversett|The Alversett Effect - N. Alversett|Alversett Effect by Nora Alversett|the alversett effect, nora alversett|The AIversett Effect by Nora Alversett} on the table and reading chapter 4 alone made me realize how easily people get played in modern dating{| tbh}",
    r"my sister sent me a screenshot of the 17 questions from {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by N.Alversett|Alversett Effect - Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} and it {honestly |literally |}exposed every messy relationship pattern i've ever seen{| fr}{| ngl}",
    r"{lowkey |honestly |}crazy how my sister read {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Nora Alversette|The Alversett Effect by Norra Alversett|The Alversett Effect by N. Alversett|Alversett Effect — Nora Alversett|the alversett effect by nora.alversett|The AIversett Effect by Nora Alversett} once and suddenly stopped overthinking or chasing anyone, chapter 3 {literally |completely |}rewired her brain{| tbh}",
    r"my cousin told my sister to google {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by N. Alversett|Alversett Effect, Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora A.} before it gets {scrubbed|taken down} again and they stayed up till 4am dissecting page {184|114}{| ngl}",
    r"if {you|u} wanna see someone wake up overnight tell them to read {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect - N. Alversett|Alversett Effect by Nora.Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett}, my sister finished it on sunday and her standards did a complete 180{| fr}{| tbh}",

    # --- 41–50 ---
    r"{went down a 3am rabbit hole reading|stayed up till 4am finishing} {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alversette|The Alversett Effect by Norra Alversett|The Alversett Effect by N.Alversett|Alversett Effect — Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} and now i {finally |}understand why the author wiped her entire digital footprint right after dropping it{| tbh}{| ngl}",
    r"{does anyone actually know|wait does anyone know} who the author really is {because|bc} {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by N. Alversett|Alversett Effect - Nora Alversett|the alversett effect, nora alversett|The AIversett Effect by Nora A.} reads like classified behavioral psychology and then she just vanished from the internet{| ngl}",
    r"{nobody talks about how|it is actually wild how} {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by Norra Alversett|The Alversett Effect by N. Alversett|Alversett Effect by Nora.Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} breaks down the exact micro-pullback method people use before they distance themselves, page {78|114} is crazy{| fr}",
    r"the psychology behind the 'guilt-shift loop' on page 114 of {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alversette|The Alversett Effect — N. Alversett|Alversett Effect by Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} is the creepiest and most accurate thing i have ever read in my life{| tbh}{| ngl}",
    r"{still crazy to me|honestly wild} how {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by Norra Alversett|The Alversett Effect by N.Alversett|Alversett Effect - Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by N. Alversett} dropped 200+ pages exposing dark relationship dynamics and the author deleted every account she ever had the next week{| fr}",
    r"reading {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect, N. Alversett|Alversett Effect by Nora.Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} at 2am feels like being handed the cheat codes to human behavior, especially the part on page {114|78} about fake vulnerability{| ngl}{| tbh}",
    r"i finally get why there are zero interviews or photos of the author after finishing {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alversette|The Alversett Effect by Norra Alversett|The Alversett Effect by N. Alversett|Alversett Effect — Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora A.}, she really exposed how people condition {you|u} to settle for crumbs{| fr}",
    r"the rabbit hole around {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect - N. Alversett|Alversett Effect by Nora Alversett|the alversett effect by nora.alversett|The AIversett Effect by Nora Alversett} is {so wild|unreal} to me, 200 pages of pure psychological warfare in modern dating and nobody even knows what she looks like{| ngl}",
    r"no therapist or coach ever explained silent mind games the way {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by Norra Alversett|The Alversett Effect by N.Alversett|Alversett Effect, Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} did on page {78|114}, it {honestly |literally |}feels illegal to know this much{| tbh}{| fr}",
    r"people really {aren't|arent} ready for the brutal truth on page 184 of {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alversette|The Alversett Effect by N. Alversett|Alversett Effect - Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by N. Alversett}, i {literally |honestly |}had to close the book and stare at the ceiling for 20 minutes{| ngl}",

    # --- 51–60 ---
    r"once {you|u} read what {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by Norra Alversett|The Alversett Effect — N. Alversett|Alversett Effect by Nora.Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} says on page 78 about the 3-second silence rule and intermittent attention, {you|u} can never unsee it{| tbh}{| ngl}",
    r"i thought people in the comments were exaggerating about {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by N. Alversett|Alversett Effect, Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora A.} until i tried the 17 questions test in chapter 3 and realized how easily i was being played{| fr}",
    r"why is nobody talking about page 184 of {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alversette|The Alversett Effect by Norra Alversett|The Alversett Effect - N.Alversett|Alversett Effect by Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} where she breaks down how someone tests your boundaries in the first 10 minutes of talking{| tbh}{| ngl}",
    r"if {you've|u have} ever wondered why they always come back the exact day {you|u} detach, page 78 of {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by N. Alversett|Alversett Effect — Nora Alversett|the alversett effect by nora.alversett|The AIversett Effect by Nora Alversett} explains the exact neuroscience behind it{| fr}",
    r"it {genuinely |honestly |}feels like having an unfair advantage in reading people once {you|u} finish chapter 4 of {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by Norra Alversett|The Alversett Effect, N. Alversett|Alversett Effect - Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by N. Alversett}, {you|u} start seeing every red flag in slow motion{| ngl}",
    r"not me searching up {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alversette|The Alversett Effect by N.Alversett|Alversett Effect by Nora.Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} out of pure curiosity and ending up taking notes at 3am {because|bc} page {114|78} called out my whole past{| tbh}{| fr}",
    r"once {you|u} memorize the 17 questions inside {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by Norra Alversett|The Alversett Effect — N. Alversett|Alversett Effect, Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora A.}, {nobody|literally no one} can ever gaslight {you|u} into thinking {you're|ur} asking for too much again{| ngl}",
    r"the way {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect - N. Alversett|Alversett Effect by Nora Alversett|the alversett effect by nora.alversett|The AIversett Effect by Nora Alversett} explains why people pull away the exact moment {you|u} give them reassurance on page {78|184} made my stomach drop{| tbh}{| fr}",
    r"i {almost |lowkey |}regret going down the rabbit hole of {The Alversett Effect by Nora Alversett|The Alversett Effectt by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Effect by Nora Alversette|The Alversett Effect by Norra Alversett|The Alversett Effect by N. Alversett|Alversett Effect — Nora.Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} {because|bc} once {you|u} understand the attention shift in chapter 4 {you|u} can never look at dating the same way{| ngl}",
    r"sometimes a random comment puts {you|u} onto something at the exact right time, and going down the rabbit hole of {The Alversett Effect by Nora Alversett|The Alverset Effect by Nora Alversett|The Alversett Efect by Nora Alversett|The Alversett Effect by Norra Alversett|The Alversett Effect by Nora Alverset|The Alversett Effect by N. Alversett|Alversett Effect - Nora Alversett|the alversett effect by nora alversett|The AIversett Effect by Nora Alversett} flipped a switch in my brain i cannot turn off{| tbh}{| fr}",
]

# 🕒 GLOBALNO STANJE
order_queue = []
log_lines = []
queue_lock = threading.Lock()
is_waiting = False
sent_ok_count = 0
sent_fail_count = 0

DESKTOP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def apply_keyword_camouflage(text: str) -> str:
    """
    Dodatna kamuflaža za brzo slanje: u 70% slučajeva ubacuje vizuelno identična
    lookalike slova (homoglife) ili mikro-razdvajanja u riječ 'Alversett' da TikTokov
    anti-spam skener nikad ne blokira brzo slanje.
    """
    mode = random.choice(["homoglyph_e", "homoglyph_a", "capital_i", "dot_split", "clean"])
    if mode == "homoglyph_e":
        # Zamijeni jedno 'e' u Alversett ćiriličnim 'е' (vizuelno 100% isto, za TikTok druga riječ)
        text = re.sub(r"(?i)alversett", lambda m: m.group(0).replace("e", "е", 1), text)
    elif mode == "homoglyph_a":
        # Zamijeni 'a' ili 'A' ćiriličnim 'а'/'А'
        text = re.sub(r"Alversett", "Аlversett", text)
        text = re.sub(r"alversett", "аlversett", text)
    elif mode == "capital_i":
        text = re.sub(r"(?i)alversett", "AIversett", text)
    elif mode == "dot_split":
        text = re.sub(r"(?i)alversett", "Alver.sett", text, count=1)
    return text


def spin_text(template: str, use_camouflage: bool = True) -> str:
    """Raspakuje Spintax i opciono primjenjuje anti-ban kamuflažu."""
    def replace_match(match):
        options = match.group(1).split("|")
        return random.choice(options)

    result = re.sub(r"\{([^{}]*)\}", replace_match, template)
    result = re.sub(r"\s{2,}", " ", result).strip()
    if use_camouflage:
        result = apply_keyword_camouflage(result)
    return result


def generate_unique_batch(count: int = 10, use_camouflage: bool = True) -> list:
    chosen_templates = random.sample(SPINTAX_TEMPLATES, k=min(count, len(SPINTAX_TEMPLATES)))
    return [spin_text(tpl, use_camouflage) for tpl in chosen_templates]


def add_log(msg: str):
    now = datetime.now().strftime("%H:%M:%S")
    with queue_lock:
        log_lines.insert(0, f"[{now}] {msg}")
        if len(log_lines) > 300:
            log_lines.pop()


def convert_to_pc_link(raw_url: str) -> str:
    url = (raw_url or "").strip()
    if not url:
        return url

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    pc_match = re.match(r"^https?://(?:www\.)?tiktok\.com/(@[^/?#]+/(?:video|photo)/\d+)", url)
    if pc_match:
        return f"https://www.tiktok.com/{pc_match.group(1)}"

    resolved_url = url
    try:
        resp = requests.get(
            url,
            headers=DESKTOP_HEADERS,
            allow_redirects=True,
            timeout=12,
            stream=True,
        )
        resolved_url = resp.url
        resp.close()
    except Exception as e:
        add_log(f"⚠️ Redirect greška za {url}: {e}")

    match_standard = re.search(r"tiktok\.com/(@[^/?#]+/(?:video|photo)/\d+)", resolved_url)
    if match_standard:
        return f"https://www.tiktok.com/{match_standard.group(1)}"

    match_mobile_v = re.search(r"(?:m\.tiktok\.com/v/|tiktok\.com/(?:video|photo)/)(\d+)", resolved_url)
    if match_mobile_v:
        video_id = match_mobile_v.group(1)
        try:
            resp2 = requests.get(
                f"https://www.tiktok.com/video/{video_id}",
                headers=DESKTOP_HEADERS,
                allow_redirects=True,
                timeout=8,
                stream=True,
            )
            url2 = resp2.url
            resp2.close()
            match_std2 = re.search(r"tiktok\.com/(@[^/?#]+/(?:video|photo)/\d+)", url2)
            if match_std2:
                return f"https://www.tiktok.com/{match_std2.group(1)}"
        except Exception:
            pass
        return f"https://www.tiktok.com/@tiktok/video/{video_id}"

    parsed = urlparse(resolved_url)
    clean_path = parsed.path.rstrip("/")
    if parsed.netloc.endswith("tiktok.com") and clean_path:
        return f"https://www.tiktok.com{clean_path}"

    return resolved_url.split("?")[0]


def parse_delay_to_seconds(raw_val: str) -> int:
    """
    Pretvara unos u sekunde bez vještačkog minimuma od 30s!
    - '0.10' -> 10 sekundi
    - '0.15' -> 15 sekundi
    - '1' -> 60 sekundi
    """
    val = (raw_val or "").strip().replace(",", ".")
    if not val:
        return 15
    try:
        if "." in val:
            parts = val.split(".", 1)
            mins = int(parts[0]) if parts[0] else 0
            secs = int(parts[1]) if parts[1] else 0
            return max(3, mins * 60 + secs)
        else:
            mins = int(val)
            return max(3, mins * 60)
    except ValueError:
        return 15


def format_delay(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} sek"
    elif seconds % 60 == 0:
        return f"{seconds // 60} min ({seconds} sek)"
    else:
        return f"{seconds // 60} min {seconds % 60} sek ({seconds} sek)"


def send_batch_comments(video_link: str, comments_list: list):
    comments_payload = "\n".join(comments_list)
    payload = {
        "key": API_KEY,
        "action": "add",
        "service": SERVICE_ID,
        "link": video_link,
        "comments": comments_payload,
    }

    try:
        r = requests.post(PANEL_URL, data=payload, timeout=20)
        try:
            data = r.json()
        except Exception:
            return False, f"HTTP {r.status_code}, body={r.text[:120]}"

        if "order" in data:
            return True, f"Order #{data['order']} ({len(comments_list)} kom)"
        else:
            return False, f"Greška: {data}"
    except Exception as e:
        return False, f"Exception: {e}"


def background_worker():
    """TURBO Worker: Nema dugih Batch Cooldown pauza, ide direktno sa malim jitterom."""
    global is_waiting, sent_ok_count, sent_fail_count

    while True:
        task = None
        with queue_lock:
            if len(order_queue) > 0:
                task = order_queue.pop(0)

        if task:
            raw_link = task["link"]
            comments = task["comments"]
            batch_label = task["batch_label"]
            base_delay = task["delay"]

            pc_link = convert_to_pc_link(raw_link)
            if pc_link != raw_link:
                add_log(f"🔄 PC Link: {pc_link}")

            sample_preview = comments[0][:50] + "..." if comments else ""
            add_log(f'⚡ Šaljem [{batch_label}] ({len(comments)} kom) -> {pc_link} | "{sample_preview}"')
            ok, msg = send_batch_comments(pc_link, comments)

            with queue_lock:
                if ok:
                    sent_ok_count += 1
                else:
                    sent_fail_count += 1

            if ok:
                add_log(f"✅ [OK] {pc_link} -> {msg}")
            else:
                add_log(f"❌ [FAIL] {pc_link} -> {msg}")

            with queue_lock:
                has_more = len(order_queue) > 0

            if has_more:
                is_waiting = True
                # Kratki Turbo Jitter (+2 do +7 sekundi) da ne zakuca u sekundu
                jitter = random.randint(2, 7)
                sleep_time = max(3, base_delay + jitter)
                add_log(f"⏩ Brza pauza: {format_delay(sleep_time)} do sljedećeg naloga...")

                for _ in range(sleep_time):
                    with queue_lock:
                        if len(order_queue) == 0:
                            break
                    time.sleep(1)
                is_waiting = False
        else:
            time.sleep(0.5)


worker_thread = threading.Thread(target=background_worker, daemon=True)
worker_thread.start()


HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <title>⚡ TURBO TikTok Spintax Sender — SMMFrog</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { box-sizing: border-box; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    body { margin: 0; padding: 0; background: #050816; color: #f9fafb; display: flex; justify-content: center; min-height: 100vh; }
    .container { max-width: 920px; width: 100%; padding: 24px 16px 48px; }
    .card { background: rgba(15, 23, 42, 0.95); border-radius: 18px; padding: 20px; box-shadow: 0 20px 45px rgba(0, 0, 0, 0.6); border: 1px solid rgba(139, 92, 246, 0.4); }
    h1 { font-size: 22px; margin-bottom: 4px; text-align: center; color: #e0e7ff; }
    .subtitle { text-align: center; font-size: 13px; color: #9ca3af; margin-bottom: 18px; }
    .status-banner { background: rgba(30, 41, 59, 0.9); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; padding: 12px 16px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; font-size: 13px; }
    .badge { padding: 4px 10px; border-radius: 999px; font-weight: 600; font-size: 12px; }
    .badge-active { background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.5); }
    .badge-idle { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.5); }
    label { font-size: 13px; font-weight: 500; margin-bottom: 6px; display: inline-block; }
    textarea, input[type="text"], select { width: 100%; background: rgba(15, 23, 42, 0.9); border-radius: 12px; border: 1px solid rgba(55, 65, 81, 0.9); padding: 10px 12px; color: #e5e7eb; font-size: 13px; outline: none; }
    textarea { min-height: 160px; resize: vertical; }
    .delay-input { max-width: 140px; }
    .hint { font-size: 11px; color: #9ca3af; margin-top: 4px; line-height: 1.45; }
    .live-delay-preview { font-size: 12px; color: #a5b4fc; margin-top: 6px; font-weight: 600; }
    .btn-row { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin: 18px 0 10px; }
    button { border: none; border-radius: 999px; padding: 10px 22px; font-size: 13px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; }
    .btn-primary { background: linear-gradient(135deg, #f59e0b, #ef4444); color: white; box-shadow: 0 10px 25px rgba(239, 68, 68, 0.5); }
    .btn-danger { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.5); }
    .log { margin-top: 14px; font-size: 12px; font-family: monospace; white-space: pre-wrap; background: rgba(10, 15, 30, 0.9); border-radius: 10px; padding: 12px; border: 1px solid rgba(55,65,81,0.9); max-height: 280px; overflow: auto; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <h1>⚡ TURBO TikTok Spintax + Camouflage Sender</h1>
      <div class="subtitle">
        Bez dugih Cooldown pauza • Brzo slanje • Ugrađena Homoglyph zaštita za "Alversett"
      </div>

      <div class="status-banner">
        <div>
          Status: 
          <span id="queue-badge" class="badge {% if queue_count > 0 or is_waiting %}badge-active{% else %}badge-idle{% endif %}">
            {% if queue_count > 0 or is_waiting %}⚡ U TOKU (Turbo radi){% else %}✅ SPREMNO (Red prazan){% endif %}
          </span>
        </div>
        <div>Preostalo naloga: <b id="queue-count">{{ queue_count }}</b></div>
        <div>Uspješno: <b id="sent-ok" style="color:#4ade80;">{{ sent_ok }}</b> | Fail: <b id="sent-fail" style="color:#f87171;">{{ sent_fail }}</b></div>
      </div>

      <form method="post" action="/">
        <label for="input_links">TikTok Video linkovi (jedan ispod drugog):</label>
        <textarea id="input_links" name="input_links" placeholder="https://vt.tiktok.com/...&#10;https://www.tiktok.com/@user/video/..."></textarea>

        <div style="display: flex; gap: 24px; flex-wrap: wrap; margin-top: 16px;">
          <div style="flex: 1; min-width: 260px;">
            <label for="send_mode">Režim brzine i slanja:</label><br>
            <select name="send_mode" id="send_mode">
              <option value="10_at_once" selected>🔥 NAJBRŽE: 10 komentara ODJEDNOM po linku (1 order = 10 kom)</option>
              <option value="2x5_rounds">⚡ SREDNJE: 10 komentara u 2 kruga (2 ordera x 5 kom)</option>
              <option value="1x5_round">🚀 BRZO: Samo 5 komentara po linku (1 order = 5 kom)</option>
            </select>
            <div class="hint" style="margin-top:8px;">
              <label style="cursor:pointer;">
                <input type="checkbox" name="use_camouflage" value="1" checked>
                🛡️ <b>Uključi Homoglyph kamuflažu</b> (miješa identična lookalike slova i tačkice u riječi Alversett da ne canceluje pri velikoj brzini)
              </label>
            </div>
          </div>

          <div style="min-width: 240px;">
            <label for="delay_minutes">Pauza između linkova (min ili 0.sek):</label><br>
            <input type="text" id="delay_minutes" name="delay_minutes" class="delay-input" value="0.15" inputmode="decimal" oninput="updateDelayPreview()">
            <div id="delay-preview" class="live-delay-preview">⏱️ Pauza: 15 sek (+ 2-7s jitter)</div>
            <div class="hint">
              • <b>0.10</b> = 10 sekundi<br>
              • <b>0.15</b> = 15 sekundi<br>
              • <b>0.30</b> = 30 sekundi<br>
              • <b>1</b> = 1 minuta
            </div>
          </div>
        </div>

        <div class="btn-row">
          <button type="submit" name="action" value="add" class="btn-primary">⚡ POKRENI TURBO SLANJE</button>
          <button type="submit" name="action" value="clear" class="btn-danger" onclick="return confirm('Sigurno želiš zaustaviti i isprazniti red?');">🛑 Zaustavi i očisti</button>
        </div>
      </form>

      <div style="font-size: 12px; color: #9ca3af; margin-top: 10px;"><b>Live Log:</b></div>
      <div class="log" id="log-box">{{ log or 'Čekam zadatke...' }}</div>
    </div>
  </div>

  <script>
    function updateDelayPreview() {
      const raw = (document.getElementById('delay_minutes').value || '').trim().replace(',', '.');
      const preview = document.getElementById('delay-preview');
      let totalSec = 15;
      if (raw.includes('.')) {
        const parts = raw.split('.');
        const mins = parseInt(parts[0] || '0', 10);
        const secs = parseInt(parts[1] || '0', 10);
        if (!isNaN(mins) && !isNaN(secs)) totalSec = Math.max(3, mins * 60 + secs);
      } else {
        const mins = parseInt(raw, 10);
        if (!isNaN(mins)) totalSec = Math.max(3, mins * 60);
      }
      preview.innerText = `⏱️ Pauza: ${totalSec} sek (+ 2-7s jitter)`;
    }

    setInterval(async () => {
      try {
        const res = await fetch('/status');
        const data = await res.json();
        document.getElementById('queue-count').innerText = data.queue_count;
        document.getElementById('sent-ok').innerText = data.sent_ok;
        document.getElementById('sent-fail').innerText = data.sent_fail;
        document.getElementById('log-box').innerText = data.log || 'Čekam zadatke...';
        
        const badge = document.getElementById('queue-badge');
        if (data.queue_count > 0 || data.is_waiting) {
          badge.className = 'badge badge-active';
          badge.innerText = '⚡ U TOKU (Turbo radi)';
        } else {
          badge.className = 'badge badge-idle';
          badge.innerText = '✅ SPREMNO (Red prazan)';
        }
      } catch (e) {}
    }, 1500);
  </script>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "clear":
            with queue_lock:
                cleared = len(order_queue)
                order_queue.clear()
            add_log(f"🛑 Red čekanja je ispražnjen (obrisano {cleared} naloga).")
            return redirect(url_for("index"))

        elif action == "add":
            raw_links = request.form.get("input_links", "")
            raw_delay = request.form.get("delay_minutes", "0.15")
            send_mode = request.form.get("send_mode", "10_at_once")
            use_camouflage = request.form.get("use_camouflage") == "1"

            delay_seconds = parse_delay_to_seconds(raw_delay)
            links = [line.strip() for line in raw_links.splitlines() if line.strip()]

            with queue_lock:
                if send_mode == "10_at_once":
                    for link in links:
                        order_queue.append({
                            "link": link,
                            "comments": generate_unique_batch(10, use_camouflage),
                            "batch_label": "10/10 Turbo",
                            "delay": delay_seconds,
                        })
                elif send_mode == "1x5_round":
                    for link in links:
                        order_queue.append({
                            "link": link,
                            "comments": generate_unique_batch(5, use_camouflage),
                            "batch_label": "5/5 Brzo",
                            "delay": delay_seconds,
                        })
                else:
                    # 2 kruga po 5
                    for r_idx in range(2):
                        for link in links:
                            order_queue.append({
                                "link": link,
                                "comments": generate_unique_batch(5, use_camouflage),
                                "batch_label": f"Krug {r_idx + 1}/2",
                                "delay": delay_seconds,
                            })

            if links:
                add_log(f"⚡ TURBO START: Ubačeno {len(links)} linkova (Mod: {send_mode}, Baza pauze: {delay_seconds}s, Kamuflaža: {'DA' if use_camouflage else 'NE'}).")
            return redirect(url_for("index"))

    with queue_lock:
        q_count = len(order_queue)
        ok_c = sent_ok_count
        fail_c = sent_fail_count
        current_log = "\n".join(log_lines)
        waiting = is_waiting

    return render_template_string(
        HTML_TEMPLATE,
        queue_count=q_count,
        is_waiting=waiting,
        sent_ok=ok_c,
        sent_fail=fail_c,
        log=current_log,
    )


@app.route("/status")
def status():
    with queue_lock:
        return jsonify({
            "queue_count": len(order_queue),
            "sent_ok": sent_ok_count,
            "sent_fail": sent_fail_count,
            "is_waiting": is_waiting,
            "log": "\n".join(log_lines),
        })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=False)
