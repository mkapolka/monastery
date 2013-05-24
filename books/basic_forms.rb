################################################################################
#                                                                              #
# A small catalogue of simple forms. Good for using as scratch paper.          #
#  Unknown origin.                                                             #
#                                                                              #
################################################################################

module Forms
   form :animal do
      contains :blood, :heart, :brain, :stomach, :skeleton
   end

   form :mouse do
      like_a :animal

      name "a field mouse"
      is :small, :soft, :fuzzy
   end

   form :mouse_stomach do
      like_a :stomach #but
      name "a mouse's stomach"
   end

   form :bear do
      like_a :animal
      is :fuzzy, :container, :alive
      @name = "a bear"
      contains :stomach
   end

   form :tea_kettle do
      is :hard, :medium, :container
      @name = "a tea kettle"
   end

   form :player do
      is :Player_Soul
      @name = "The player"
   end
end
