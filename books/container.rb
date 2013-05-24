module Properties
   class Container < Property
      attr_accessor :contents

      def initialize
          super;
          @contents = [];
      end

      def [](o)
         return @contents[o];
      end

      def []=(k,v)
         @contents[k] = v;
      end

      def delete(what)
         @contents.delete(what);
      end

      def remove(which)
         @contents[@contents.index(which)] = nil;
      end

      def describe()
          "contains " + @contents.reduce(""){ |p,x| p + x.name + " and " }[0..-6]
      end
   end
end

#Container-related methods
class Noun
	def contains(*things)
		is :container
		things.each do |thing|
			new_thing = spawn thing
         add(new_thing) if not new_thing.nil?
		end
	end

	def contains?(what)
		return false if not container?
		return container.contents.index(what) > 0
	end

	def contains_with_property?(property)
		return false if not container?
		return !(container.contents.find{ |x| x.send(property.to_s + "?") }).nil?
	end

	def contents
		return nil if not self.container?
		return self.container.contents
	end

	def touching
		return me.parent.contents if not me.parents.is_room?
	end

   def add_to_container(what)
      if not what.container?
         puts "Tried to add something to #{self.name} even though it's not a container!";
         return;
      else
         what.container.contents << self;
         self.do(:added_to, self, what);
         what.do(:added, what, self);
      end
   end

   def add(what)
      what.add_to_container(self);
   end

   def remove_from_container(what)
      if not what.container?
         puts "Tried to remove something from #{self.name} even though it's not a container!";
         return;
      else
         what.container.contents.delete(what);
         self.do(:removed_from, self, what);
         what.do(:removed, what, self);
      end
   end

   def remove(what)
      what.remove_from_container(self);
   end

   def move_to_container(container)
      parent = container;
   end

   def parent=(container)
      if not @parent.nil?
         @parent.remove(self);
      end
      @parent = container;
      self.add_to_container(container);
   end
end
