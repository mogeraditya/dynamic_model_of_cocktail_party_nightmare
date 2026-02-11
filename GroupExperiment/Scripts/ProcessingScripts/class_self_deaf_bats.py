"""This module contains the code that describes a Bat object and its behaviours"""

from agents.class_bats import Bat
from agents.class_sounds import DirectSound
from supporting_files.utilities import call_directionality_factor


class CannotHearSelfEchoBat(Bat):
    def __init__(self, parameters_df, output_dir):
        super().__init__(parameters_df, output_dir)

    def given_sound_objects_return_sounds_at_bat_position(
        self, current_time, sound_objects
    ):
        """given sounds generate list of sounds that a bat can hear
        HERE THE BAT CANNOT HEAR SELF ECHO

        Args:
            current_time (float): Time, in seconds, for which the simualtion has been running.
            sound_objects (list): List containing all active sounds in the simulation
            detect_self_call (Bool): If true, add self call to detected, else, skip self call.

        Returns:
            list: sound detections given time.
        """
        array_of_sound_detections = []
        # if bat is calling it shouldnt hear anything
        is_bat_calling = (
            current_time < self.emit_times[-1] + self.parameters_df["CALL_DURATION"]
        )
        if is_bat_calling:
            return array_of_sound_detections
        for sound in sound_objects:
            # sound.update(current_time)

            is_sound_active = sound.active

            is_sound_self_call = sound.emitter_id == self.id and isinstance(
                sound, DirectSound
            )
            is_sound_self_echo = sound.emitter_id == self.id

            is_sound_reflected_from_self = sound.reflected_from == f"bat_{self.id}"

            if (
                not is_sound_active
                or is_sound_self_call
                or is_sound_reflected_from_self
                or is_sound_self_echo
            ):
                continue

            # sound can only be detected if bat is inside the sound wave
            if sound.contains_point(self.position):
                received_spl = sound.spl_at_receiver(self.position)

                angle_between_sound_and_bat = sound.direction_vector.angle_between(
                    self.position
                )
                hearing_directionality = call_directionality_factor(
                    a=self.parameters_df["HEARING_DIRECTIONALITY"],
                    theta=angle_between_sound_and_bat,
                )

                received_spl += hearing_directionality
                is_sound_audible = (
                    received_spl > self.parameters_df["HEARING_THRESHOLD"]
                )

                if not is_sound_audible:
                    continue
                array_of_sound_detections.append(
                    self.convert_sound_to_dictionary(sound, current_time, received_spl)
                )
        return array_of_sound_detections
