Imagine a bad guy (a thief or criminal) is planning to break into a big museum.

To pull this off without getting caught by police guards, the thief does three sneaky things:

1. **Checks the museum doors at night** to see which lock is loose.
2. **Sends a fake letter with a fake website link** to a museum guard to steal their keycard password.
3. **Uses cheap burner phones** that they throw away every few hours so the police cannot track where they are standing.

If the police only look at the lock, they think: *"Maybe the wind shook the door."*

If they only look at the letter, they think: *"Just junk mail."*

If they only look at the phone tower, they think: *"Someone dropped a phone."*

Our system connects all three clues to say: **"Wait! That is the exact same thief doing all three things right now!"**

To teach our computer how to catch these clues, we feed it **3 special collections of information (called Datasets)**.

---

### Dataset 1: The "Digital Lock Tester" (UNSW-NB15)

* **What it is in simple words:** A big diary of internet traffic that records computers talking to each other. It contains both normal, polite internet visits and hackers violently shaking digital doors to see which door opens.
* **Why we use it:** To teach our computer how a digital break-in or scanning probe looks compared to a normal person browsing YouTube.

**Important Keywords & What They Mean:**

* **IP Address (Internet Protocol Address):**
* *What it means:* The home address of a computer on the internet.
* *Example:* Just like your home has a street address (`Flat 204, Rose Apartments`), a computer has an address like `192.168.1.50`.


* **Port:**
* *What it means:* Specific doors inside that computer house.
* *Example:* Door 80 is the front door for websites, Door 25 is the mail slot for emails, and Door 502 is the back door controlling water pumps or electricity.


* **Port Scan (Reconnaissance):**
* *What it means:* A thief walking down a hotel hallway quickly turning every doorknob to see which room is unlocked.
* *Example:* Checking 1,000 doors in 2 seconds to find an open one.


* **Packet & Byte Count:**
* *What it means:* Packets are small envelopes of data; bytes are how heavy the envelope is.
* *Example:* If someone sends 10,000 heavy envelopes at 3:00 AM, something suspicious is happening.


* **TTL (Time to Live):**
* *What it means:* A countdown timer on an envelope so it doesn't bounce around the internet forever.



---

### Dataset 2: The "Fake Trap Link" (Phishing URL Corpus)

* **What it is in simple words:** A huge list of website names (links). Some are safe (like `google.com`), and others are fake trick links made by bad guys to steal passwords.
* **Why we use it:** Bad guys don't break in only using code; they trick real humans into clicking bad links to let them inside.

**Important Keywords & What They Mean:**

* **URL (Uniform Resource Locator):**
* *What it means:* The nickname/link you click to go to a web page.
* *Example:* `[https://www.wikipedia.org](https://www.wikipedia.org)`.


* **Phishing:**
* *What it means:* Throwing a fishing hook with fake bait to trick someone.
* *Example:* An email saying *"URGENT: Click here to verify your bank password!"* with a fake link.


* **Domain & Hostname:**
* *What it means:* The main name of the website.
* *Example:* In `google.com`, the domain is `google`.


* **Typosquatting (Look-alike link):**
* *What it means:* Misspelling a trusted name to fool your eyes.
* *Example:* Instead of `netflix.com`, the bad guy makes `netfIix-login.com` (using a capital `I` instead of `l`).


* **N-Gram:**
* *What it means:* Cutting a word into small letter chunks so a computer can see strange letter patterns.
* *Example:* The word `secure` split into 3-letter chunks is `sec`, `ecu`, `cur`, `ure`.



---

### Dataset 3: The "Burner Phone & Secret Footsteps" (Telecom CDR)

* **What it is in simple words:** A diary kept by mobile phone towers recording who made phone calls, which handset they used, and which tower their phone touched.
* **Why we use it:** Bad guys don't keep one phone with their real name on it. They buy cheap phones, switch SIM cards constantly, and move around secretly. This dataset catches their physical footprints.

**Important Keywords & What They Mean:**

* **CDR (Call Detail Record):**
* *What it means:* A phone company's automated receipt showing who called whom, at what time, and for how many seconds (it does *not* listen to the voice; it only checks the call receipt).


* **IMEI (International Mobile Equipment Identity):**
* *What it means:* The permanent fingerprint number of the physical plastic/metal phone handset itself.
* *Example:* Even if you throw away your SIM card, your phone body still has the exact same IMEI number.


* **SIM Card / IMSI:**
* *What it means:* The tiny chip you put inside the phone that holds your phone number.


* **IMEI Churn (Burner Phone behavior):**
* *What it means:* One person swapping lots of different SIM cards into a single phone, or using a phone once and throwing it into a dustbin.
* *Example:* A suspect using 4 different SIM cards inside 24 hours on one cheap phone.


* **Cell Tower & Co-location:**
* *What it means:* Cell towers are giant antennas on buildings. When two people are standing near each other, their phones ping the exact same tower.
* *Example:* Person A and Person B never call each other, but both of their secret phones connect to the same tower near the power station at midnight.



---

### How These Datasets Work Together (The Real Magic)

```
[ UNSW-NB15 ]           [ Phishing URLs ]          [ Telecom CDR ]
     │                         │                          │
     ▼                         ▼                          ▼
"Someone scanned a        "The same IP             "A burner phone 
 SCADA water pump."        hosted a fake link."     pinged the water pump tower."
     │                         │                          │
     └─────────────────────────┼──────────────────────────┘
                               ▼
            ╔════════════════════════════════════╗
            ║         CONNECTED IN GRAPH         ║
            ║                                    ║
            ║   Target: Suspect ACTOR_48         ║
            ║   Risk: 98% (CRITICAL ALERT)       ║
            ╚════════════════════════════════════╝

```

1. **UNSW-NB15** tells us: *"Someone is testing the lock on the back door."*
2. **Phishing URL Corpus** tells us: *"The same person created a fake login link."*
3. **Telecom CDR** tells us: *"That person's burner phone is physically standing outside the building."*

When all three datasets light up for the same suspect, our system raises a red flag so law enforcement can stop them before anything bad happens.