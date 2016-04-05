from __future__ import absolute_import
from celery import shared_task
from django.contrib.auth.models import User
from skill_match.models import Feedback
from users.models import Skill


@shared_task
def test_task():
    print("Say what again ")


@shared_task
def update_skills(player, sport):

    print("hiello there ther ")
    player = User.objects.get(id=player)
    feedback_count = Feedback.objects.filter(player=player).filter(match__sport=sport).count()
    skill = Skill.objects.filter(player=player).filter(sport=sport)

    # Update every 3 matches to keep feedback anonymous
    if feedback_count % 3 == 0:
        if skill:
            skill = skill[0]
            skill.calculate()
        else:
            skill = Skill.objects.create(player=player, sport=sport)
            skill.calculate()

        print("The newly calculated skill is {}".format(skill))

    else:
        print("Processed, but No update this time around")
