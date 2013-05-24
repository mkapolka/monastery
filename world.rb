################################################################################
#                                                                              #
# The Atlas of the Lands Surrounding the Monastery                             #
#  By Brother Took the traveler                                                #
#                                                                              #
################################################################################

module Properties
   class Room < Property
      description "is a room"
   end

   class Door < Property
      def describe
         "leads to #{@target.name}"
      end
   end
end

class Noun
   def containing_room
      p = self;
      while not p.room? and not p.parent.nil?
         p = p.parent;
      end
      return p;
   end

   def has_door_to(where)
      d = spawn :door
   end

   def contains_room(*rooms)
      rooms.each do |room|
         add spawn("room_" + room.to_s);
      end
   end
   alias :contains_rooms :contains_room
end

module Forms
   @@rooms = {};

   def self.room(name, &block)
      @@templates["room_" + name.to_s] = block;
   end

   form :world do
      name "The World"
      is :container
      contains_room :the_monastery_garden
   end

   room :the_monastery_garden do
      name "In the Monastery Garden"
      is :room
      contains :bear, :player
   end
end

def make_world
   $world = spawn :world
end
