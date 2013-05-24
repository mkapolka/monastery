################################################################################
## A Treatise on Ontology ######################################################
##  By Brother Buddy ###########################################################
################################################################################
# In this document I will propose an ontology to suit the needs of the         #
# Monastery.                                                                   #
#                                                                              #
# A Noun is the fundamental unit of being. It is a thing. A Noun has many      #
# Properties. These Properties are what give it meaning within the system of   #
# the world- Properties are what cause a Noun to react to the world around it, #
# and what allow it to act on the world.                                       #
################################################################################

class Noun
	attr_accessor :properties, :name, :parent

	#Every Noun has a name to help distinguish it from other things.
	def name(string = nil)
	 @name = string if string
	 return @name
	end

   def initialize
      @name = "#{self.class}"
      @properties = {};
   end

	 def inspect
		return self.name
	 end

	 #Nouns can have things done to them, but their reaction to those events will
	 # be determined the properties of the noun.
   def do(what, *args)
      @properties.each_pair do |key, prop|
				 what = what.to_sym;
				 next if prop.events.nil?
             prop.instance_exec(args, &prop.events[what]) if not prop.events[what].nil?
             #prop.events[what].call(*args) if not prop.events[what].nil?;
      end
   end

   def destroy
      unless self.parent.nil?
         self.parent.container.remove(self)
      else
         puts "Cannot destroy #{self.name} as it doesn't have a parent.";
      end
   end
   
	 #The Properties of an object are constantly in flux. They may be made or
	 # unmade at any time, according to the situation of the object.
   def make(*new_props)
			new_props.each do |property|
				begin
					prop_class = Properties.get_property(property)
				rescue => exception
					puts "Invalid property name: #{property.to_s}";
               #puts exception.backtrace[0..5];
					next;
				end

            property = property.downcase

				unless properties[property].nil?
					 properties[property].count += 1 
				else 
					 a = properties[property] = prop_class.new
					 a.do(:make, self);
					 a.noun = self;
					 a.count = 1;

					 prop_accessor property
				end
			end
   end
   alias :is :make;
   alias :becomes :make

	 def unmake(*props)
      props.flatten!
		props.each do |prop|
			begin
				prop_class = Properties.get_property(prop);
			rescue => exception
				puts "Invalid property name: #{prop.to_s}"
            #puts exception.backtrace[0..5];
				next;
			end
			prop = prop.downcase;

			unless properties[prop].nil?
				properties[prop].count -= 1;
				if (properties[prop].count <= 0)
					properties[prop].do(:unmake, self);
					properties.delete prop;
				end
			else
				puts "#{self.name} wasn't #{prop} to begin with.";
			end
		end
	 end

    def get_property(which)
      return properties[which];
    end

	 #We can test whether a Noun exemplifies a certain property in this manner:
	 # "noun.property?" where 'property' is the name of the property. For example,
	 # if we want to test whether a bear is fuzzy, we might call bear.fuzzy? The 
	 # answer to this question will reveal whether or not the bear is fuzzy. We can
	 # also access the object pertaining to that particular property with the 
	 # phrase "noun.property". For instance, if we want to feed our bear by adding
	 # a mouse to the belly of a bear, we might call bear.container << mouse. Both
	 # of these terms, "noun.property?" and "noun.property" are set up with the
	 # method prop_accessor. The first argument of prop_accessor is the word we will
	 # use to access the property we want, and the second term is the property's own
	 # name. If we only specify one argument we assume that we want the same word
	 # to be used for both. I.e. "bear.prop_accessor :fuzzy" will create the methods
	 # bear.fuzzy and bear.fuzzy?, whereas "bear.prop_acessor :fuzzy :wuzzy" will
	 # create the methods "bear.fuzzy" and "bear.fuzzy?", but they will poll the
	 # bear's "wuzzy" property.
	 def prop_accessor(name, prop_name = nil)
			prop_name ||= name;
			metaclass.instance_eval do
				define_method(name.downcase) do
					properties[prop_name]
				end

				define_method(name.downcase.to_s + "?") do
					!properties[prop_name].nil?
				end
			end
	 end

	 #Sometimes it is helpful to get all the properties of a Noun that share
	 # a certain type. 
   def properties_of_type(type)
      return properties.each_pair.select{ |k,v| puts "Donka: #{v}, #{v.types}"; v.types.find(type).nil? }
      #return properties.each_pair.map do |key, value|
         ##!value.types.index(type).nil? 
         #value if !value.types.index(type).nil?
      #end
   end

	 #When a method doesn't exist this one is called instead, which allows us to
	 # check for the existence of a property with the "noun.property?" syntax
	 # even if that property isn't present in the object.
   def method_missing(method, *args)
      #puts "Mizzing"
      return false if (method[-1] == "?")
      super.method_missing(method, args)
   end

   def describe
      "#{name}" + properties.values.reduce(""){ |p,x| p + " " + x.describe + " and" }[0...-4] + "."
   end

   def is?(property)
      not properties[property.downcase.to_sym].nil?;
   end

	 def like_a(what)
		p = Forms.get_template what
		instance_eval(&p) if not p.nil?
	 end

################################################################################
#                                                                              #
# Methods that exist as actions in the game fiction.                           #
#                                                                              #
################################################################################
	 def say(text, channel)
         case channel
         when :say
            puts text if self.containing_room == current_player.containing_room;
         when :do
            puts text if self == current_player
         end
	 end

    def detect(wavelength=:look)
      out = []
      @parent.contents.each do |x|
         out.push(x) unless x.invisible?
      end
      return out
    end

    def visible_objects
      return detect :look
    end
end
