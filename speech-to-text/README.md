Contains Instructions for Running Speech-to-Text

Takes in an audio file and creates phonetic transcription for Shimon

- SPEECH DETECTION
    - USING POCKETSPHINX
        - Installing SpeechRecognition
            - `pip install SpeechRecognition`
            - `pip install pydub`
        - Installing PocketSphinx
            - NOTE:
                - There will be an error if you try `pip3 install pocketsphinx`, so try the following steps instead

            - git clone --recursive https://github.com/bambocher/pocketsphinx-python
            - `cd pocketsphinx-python`
            - Edit file:
                - `vim deps/sphinxbase/src/libsphinxad/ad_openal.c`
            - Change
                #include <al.h>
                #include <alc.h>
                to
                #include <OpenAL/al.h>
                #include <OpenAL/alc.h>
            - python setup.py install

    - USING GOOGLE CLOUD SPEECH

- IPA RESOURCES (PHONETICS)
    - https://www.phon.ucl.ac.uk/home/wells/ipa-unicode.htm#numbers
    - https://github.com/mphilli/English-to-IPA
        - `pip3 install git+https://github.com/mphilli/English-to-IPA.git`
    - https://pypi.org/project/ipapy/
        - no use right now...
        - `pip3 install ipapy`