################################################################################
# A Treatise on Ontology, Part 2                                               #
# By Brother Buddy                                                             #
#                                                                              #
# Properties are the substance of the world. They are what describe objects    #
# not only in the physical sense of what they are, but also in terms of what   #
# they do.                                                                     #
################################################################################
module Properties
   def get_property(name)
      begin
         return const_get(Properties::constants.find{ |x| x.downcase == name.downcase });
         #return const_get(name) if not const_get(name).nil?
      rescue
         return const_get(name.capitalize)
      end
   end

	class Property
		 attr_accessor :count, :value, :noun
       class_attribute :events, :types, :revelead_by
      alias :me :noun

      @@properties = {};

      def self.properties
         return @@properties;
      end

		 class << self
          attr_reader :events, :types, :revealed_by
          @events = {};
		 end

       types = [];

		 def initialize
				@count = 0;
		 end

		 def events
			self.class.events
		 end

		 def self.events
			return @events
		 end

		 def describe()
				return ""
		 end

		 def self.description(string)
			 define_method(:describe) do
					string
			 end
		 end

       def do(event, *args)
         self.class.events[event.to_sym].call(args)
       end

		 def self.upon(event, &block)
			 define_method(event, block);
			 @events ||= {};
			 @events[event.to_sym] = block;
		 end

		 def self.types(*args)
				return super if args.length==0
				@types ||= [];
				args.each do |x|
					 @types.push(x) if @types.index(x).nil?
				end
		 end
       
       def types
         return self.types;
       end

      def self.type(args)
         self.types(args);
      end

		 def self.revealed_by(*args)
				return @revealed_by if args.length == 0;
				@revealed_by ||= [];
				args.each do |x|
					@revealed_by.push(x) if @revealed_by.index(x).nil?
				end
		 end

		 def types
				self.class.class_eval do
					 @types
				end
		 end

		 def do(what, *args)
				return if self.events.nil?
            self.instance_exec *args, &self.events[what] unless events[what].nil?
		 end
	end

	def self.the_following_are(*new_types, &block)
		old_properties = Properties.constants;
		yield
		new_properties = Properties.constants - old_properties;
		new_properties.each do |x|
			 Properties.const_get(x).types new_types
		end
	end
end
