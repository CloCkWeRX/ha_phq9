# Home Assistant PHQ-9 Integration

This integration provides a PHQ-9 device for each Person entity in Home Assistant, with sensors for each of the nine questions.

PHQ-9 is a 9-item questionnaire used to screen for, and assess the severity of depression.

## Why?

Many home assistant integrations focus on sensing the physical environment, but with the exception of wearables, not many assess the state of a person beyond "sleeping" or "active"; potentially a few others for detected activities.

In academia there are a [large](https://pmc.ncbi.nlm.nih.gov/articles/PMC12290141/) [number](https://physionet.org/content/globem/1.1/) of projects to [assess](https://studentlife.cs.dartmouth.edu/dataset.html) and [measure](https://zenodo.org/records/546113).

Unfortunately, large corporate entities use [this kind of research approach unethically](https://www.theguardian.com/technology/2014/jun/30/facebook-emotion-study-breached-ethical-guidelines-researchers-say), strictly to further their own goals.

This is an experiment to explore what using self-assessment, tied to automation can beneficially do for laypersons; where tooling operates in your interests and as an extension of your agency.

## Considerations for use

This project is an attempt to provide sensors, and [classification only as per the literature](https://www.hiv.uw.edu/page/mental-health-screening/phq-9).

It is not:

* Advice
* Diagnosis

The questions asked are sensitive; do *not* use this without the consent of all parties in your home assistant installation.

## Example Automations

### Severe Score Notification

This automation sends a persistent notification when the score interpretation for a person becomes "Moderately Severe".

```yaml
automation:
  - alias: "PHQ-9 Moderately Severe Score Notification for Jane"
    trigger:
      - platform: state
        entity_id: sensor.phq_9_score_interpretation_jane # Assumes a person named Jane
        to: "Moderately Severe"
    action:
      - service: persistent_notification.create
        data:
          title: "PHQ-9 Score is Moderately Severe for Jane"
          message: "The PHQ-9 score for Jane is Moderately Severe. [Watch this video for support](https://www.youtube.com/watch?v=d6v3vKeg1Ws)"
```

### Weekly Reset and Reminder

This automation runs every Sunday at 8:00 PM. It resets all the PHQ-9 answers for a person to the default and sends a notification to remind them to update their answers.

```yaml
automation:
  - alias: "Weekly PHQ-9 Reset and Reminder for Jane"
    trigger:
      - platform: time
        at: "20:00:00"
    condition:
      - condition: time
        weekday:
          - sun
    action:
      - service: input_select.select_option
        target:
          entity_id:
            - input_select.phq_9_question_1_jane
            - input_select.phq_9_question_2_jane
            - input_select.phq_9_question_3_jane
            - input_select.phq_9_question_4_jane
            - input_select.phq_9_question_5_jane
            - input_select.phq_9_question_6_jane
            - input_select.phq_9_question_7_jane
            - input_select.phq_9_question_8_jane
            - input_select.phq_9_question_9_jane
        data:
          option: "Not at all"
      - service: input_select.select_option
        target:
          entity_id: input_select.phq_9_difficulty_jane
        data:
          option: "Not difficult at all"
      - service: persistent_notification.create
        data:
          title: "PHQ-9 Weekly Reminder"
          message: "It's time to update your PHQ-9 answers for the week, Jane."
```


## Citation

Kroenke K, Spitzer RL, Williams JB. The PHQ-9: validity of a brief depression severity measure. J Gen Intern Med. 2001 Sep;16(9):606-13. doi: 10.1046/j.1525-1497.2001.016009606.x. PMID: 11556941; PMCID: PMC1495268.
